from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import Project, Shot
from .storage import load_project, save_project, ROOT
import os
from fastapi.responses import FileResponse
from .ffmpeg_tools import make_proxy
import time

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
    if not shot.video_path:
        raise HTTPException(400, "shot.video_path missing or file not found")
    input_path = shot.video_path
    if not os.path.isabs(input_path):
        input_path = os.path.join(ROOT, input_path)
    if not os.path.exists(input_path):
        raise HTTPException(400, "shot.video_path missing or file not found")
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


