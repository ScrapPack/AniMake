from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from .models import Project, Shot
from .storage import load_project, save_project, ROOT
import os
from fastapi.responses import FileResponse
from .ffmpeg_tools import make_proxy
import time
import asyncio
from .jobs import create_job, get_job
from workers.vace_runner import run_vace as vace_run

app = FastAPI(title="Animation Composer API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/project", response_model=Project)
def get_project():
    return load_project()

@app.post("/project", response_model=Project)
def set_project(p: Project):
    save_project(p)
    return p

@app.get("/shots", response_model=list[Shot])
def get_shots():
    return load_project().shots

@app.post("/shots", response_model=Shot)
def add_shot(shot: Shot):
    p = load_project()
    if any(s.id == shot.id for s in p.shots):
        raise HTTPException(400, f"Shot {shot.id} exists")
    p.shots.append(shot)
    save_project(p)
    return shot

@app.patch("/shots/{shot_id}", response_model=Shot)
def patch_shot(shot_id: str, patch: Shot):
    p = load_project()
    for i, s in enumerate(p.shots):
        if s.id == shot_id:
            p.shots[i] = patch
            save_project(p)
            return patch
    raise HTTPException(404, f"Shot {shot_id} not found")

@app.get("/proxies/{shot_id}")
def get_proxy(shot_id: str):
    p = load_project()
    shot = next((s for s in p.shots if s.id == shot_id), None)
    if not shot:
        raise HTTPException(404, f"Shot {shot_id} not found")
    input_path = shot.active_video or shot.video_path
    if not input_path:
        raise HTTPException(400, "no active or source video for shot")
    if not os.path.isabs(input_path):
        input_path = os.path.join(ROOT, input_path)
    if not os.path.exists(input_path):
        raise HTTPException(400, "video file not found for shot")
    prox_dir = os.path.join(ROOT, "cache", "proxies")
    prox_path = os.path.join(prox_dir, f"{shot.id}.mp4")
    out = make_proxy(input_path, prox_path)
    return FileResponse(out, media_type="video/mp4")

@app.get("/proxies/{shot_id}/status")
def get_proxy_status(shot_id: str):
    p = load_project()
    shot = next((s for s in p.shots if s.id == shot_id), None)
    if not shot:
        raise HTTPException(404, f"Shot {shot_id} not found")
    input_path = shot.video_path or ""
    if input_path and not os.path.isabs(input_path):
        input_path = os.path.join(ROOT, input_path)
    prox_dir = os.path.join(ROOT, "cache", "proxies")
    prox_path = os.path.join(prox_dir, f"{shot.id}.mp4")
    exists = os.path.exists(prox_path) and os.path.getsize(prox_path) > 0
    size = os.path.getsize(prox_path) if exists else 0
    mtime = os.path.getmtime(prox_path) if exists else None
    return {
        "exists": exists,
        "size": size,
        "mtime": mtime,
        "proxy_path": prox_path,
        "input_path": input_path,
        "has_input": bool(input_path) and os.path.exists(input_path),
    }


def _dummy_stage(logger, duration_s: int = 5):
    steps = 10
    for i in range(steps):
        time.sleep(duration_s / steps)
        logger(int((i + 1) * 100 / steps), f"step {i + 1}/{steps}")
    return {"ok": True}


@app.post("/run/{stage}/{shot_id}")
async def run_stage(stage: str, shot_id: str):
    p = load_project()
    if not any(s.id == shot_id for s in p.shots):
        raise HTTPException(404, f"Shot {shot_id} not found")
    job = create_job(_dummy_stage, kwargs={"duration_s": 4})
    loop = asyncio.get_running_loop()
    asyncio.create_task(job.run(loop))
    return {"job_id": job.id}


@app.get("/jobs/{job_id}")
def job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")
    return {"id": job.id, "status": job.status, "result": job.result, "error": job.error}


@app.websocket("/jobs/{job_id}/logs")
async def job_logs(ws: WebSocket, job_id: str):
    await ws.accept()
    job = get_job(job_id)
    if not job:
        await ws.send_json({"pct": 100, "msg": "error: job not found"})
        await ws.close()
        return
    while True:
        evt = await job._queue.get()  # noqa: SLF001
        await ws.send_json(evt)
        if job.status in ("done", "error") and job._queue.empty():  # noqa: SLF001
            await ws.close()
            break


def _shot_dir(shot_id: str) -> str:
    return os.path.join(ROOT, f"shots/{shot_id}")


@app.post("/run/vace/{shot_id}")
async def run_vace_stage(shot_id: str):
    p = load_project()
    shot = next((s for s in p.shots if s.id == shot_id), None)
    if not shot:
        raise HTTPException(404, "shot not found")
    if not shot.video_path:
        raise HTTPException(400, "shot.video_path required as plate")

    def _fn(logger):
        logger(5, "starting vace")
        plate = shot.video_path
        if not os.path.isabs(plate):
            plate = os.path.join(ROOT, plate)
        out = vace_run(_shot_dir(shot_id), (shot.stages.vace or {}).model_dump() if shot.stages.vace else {}, plate)
        # Promote produced clip as active video
        try:
            rel_out = os.path.relpath(out.get("video", ""), ROOT)
            proj = load_project()
            for i, s in enumerate(proj.shots):
                if s.id == shot_id:
                    proj.shots[i].active_video = rel_out
                    break
            save_project(proj)
            logger(98, "active video updated")
        except Exception as _:
            logger(98, "warning: failed to update active video")
        logger(95, "vace done")
        return out

    loop = asyncio.get_running_loop()
    job = create_job(_fn)
    asyncio.create_task(job.run(loop))
    return {"job_id": job.id}
