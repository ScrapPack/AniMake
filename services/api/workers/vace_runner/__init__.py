import os, subprocess, glob
from pathlib import Path
from typing import Dict


def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)


def _simulate_block(input_video: str, out_video: str):
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_video,
        "-c:v",
        "libx264",
        "-crf",
        "18",
        "-c:a",
        "aac",
        out_video,
    ]
    subprocess.run(cmd, check=True)


def _extract_line_keys(input_video: str, out_dir: str, every_n: int = 12):
    ensure_dir(out_dir)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_video,
        "-vf",
        f"fps=1/{every_n},edgedetect=low=0.1:high=0.2",
        f"{out_dir}/%03d.png",
    ]
    subprocess.run(cmd, check=True)


def run_vace(shot_dir: str, params: Dict, plate_path: str) -> Dict:
    vdir = os.path.join(shot_dir, "vace")
    kdir = os.path.join(shot_dir, "keys", "line")
    ensure_dir(vdir)
    ensure_dir(kdir)
    existing = sorted(glob.glob(os.path.join(vdir, "block_v*.mp4")))
    idx = len(existing) + 1
    out_mp4 = os.path.join(vdir, f"block_v{idx}.mp4")

    from services.api.app.config import VACE_ENABLED, VACE_CLI

    if VACE_ENABLED:
        cmd = VACE_CLI.split() + [
            "--task",
            params.get("preset", "pose"),
            "--video",
            plate_path,
            "--out",
            out_mp4,
        ]
        subprocess.run(cmd, check=True)
    else:
        _simulate_block(plate_path, out_mp4)

    _extract_line_keys(out_mp4, kdir, every_n=12)
    return {"video": out_mp4, "line_keys_dir": kdir}


