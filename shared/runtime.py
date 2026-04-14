from __future__ import annotations

from pathlib import Path


APP_DIR = Path.home() / ".cache" / "music-agent"
SOCKET_PATH = APP_DIR / "musicd.sock"
PID_PATH = APP_DIR / "musicd.pid"
LOG_PATH = APP_DIR / "musicd.log"
MPV_SOCKET_PATH = APP_DIR / "mpv.sock"
MPV_PID_PATH = APP_DIR / "mpv.pid"
LOCK_PATH = APP_DIR / "musicd.lock"
STATUS_JSON_PATH = APP_DIR / "status.json"


def ensure_runtime_dir() -> Path:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    return APP_DIR
