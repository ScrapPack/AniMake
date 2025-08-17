import os, subprocess

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def make_proxy(input_path: str, proxy_path: str) -> str:
    ensure_dir(os.path.dirname(proxy_path))
    if os.path.exists(proxy_path) and os.path.getsize(proxy_path) > 0:
        return proxy_path
    cmd = [
        "ffmpeg","-y","-i",input_path,
        "-vf","scale=-2:540",
        "-c:v","libx264","-preset","veryfast","-b:v","3M",
        "-c:a","aac", proxy_path
    ]
    subprocess.run(cmd, check=True)
    return proxy_path


