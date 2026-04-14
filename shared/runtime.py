from __future__ import annotations

from pathlib import Path


APP_DIR = Path.home() / ".cache" / "music-agent"
SOCKET_PATH = APP_DIR / "musicd.sock"
PID_PATH = APP_DIR / "musicd.pid"
LOG_PATH = APP_DIR / "musicd.log"
MPV_SOCKET_PATH = APP_DIR / "mpv.sock"
LOCK_PATH = APP_DIR / "musicd.lock"


def ensure_runtime_dir() -> Path:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    return APP_DIR
