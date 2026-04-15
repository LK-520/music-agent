from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import List

from shared.models import Track
from shared.runtime import APP_DIR, ensure_runtime_dir
from shared.utils import clean_artist_name, query_tokens, run_subprocess


YTMUSIC_VENV_DIR = APP_DIR / "venvs" / "ytmusicapi"
YTMUSIC_LOCK_PATH = APP_DIR / "ytmusicapi.lock"


def is_artist_only_query(query: str) -> bool:
    tokens = query_tokens(query)
    if not tokens:
        return False
    raw = (query or "").strip()
    disallowed = {"《", "》", "-", "_", "/", "|", "feat", "ft.", "mv", "歌词", "lyric"}
    lowered = raw.lower()
    if any(token in lowered for token in disallowed):
        return False
    if len(tokens) == 1:
        return True
    if len(tokens) == 2:
        if all(token.isascii() for token in tokens):
            return True
        if max(len(token) for token in tokens) <= 4:
            return True
    return False


def _venv_python_path() -> Path:
    if os.name == "nt":
        return YTMUSIC_VENV_DIR / "Scripts" / "python.exe"
    return YTMUSIC_VENV_DIR / "bin" / "python"


def _venv_ready() -> bool:
    python_bin = _venv_python_path()
    if not python_bin.exists():
        return False
    result = run_subprocess(
        [str(python_bin), "-c", "import ytmusicapi"],
        timeout=20,
    )
    return result.returncode == 0


def _ensure_ytmusicapi_venv() -> Path | None:
    ensure_runtime_dir()
    python_bin = _venv_python_path()
    if _venv_ready():
        return python_bin
    APP_DIR.mkdir(parents=True, exist_ok=True)
    with open(YTMUSIC_LOCK_PATH, "w", encoding="utf-8") as lock_handle:
        try:
            import fcntl

            fcntl.flock(lock_handle, fcntl.LOCK_EX)
        except Exception:
            pass
        if _venv_ready():
            return python_bin
        create = run_subprocess([sys.executable, "-m", "venv", str(YTMUSIC_VENV_DIR)], timeout=180)
        if create.returncode != 0:
            return None
        install = run_subprocess(
            [str(python_bin), "-m", "pip", "install", "-q", "ytmusicapi"],
            timeout=240,
        )
        if install.returncode != 0 or not _venv_ready():
            return None
    return python_bin if python_bin.exists() else None


def search_artist_top_tracks(query: str, limit: int) -> List[Track]:
    python_bin = _ensure_ytmusicapi_venv()
    if not python_bin:
        return []
    script = r"""
import json, sys
from ytmusicapi import YTMusic

query = sys.argv[1]
limit = int(sys.argv[2])
api = YTMusic()
artists = api.search(query, filter="artists", limit=5) or []
if not artists:
    print("[]")
    raise SystemExit(0)
artist = artists[0]
data = api.get_artist(artist["browseId"])
songs = ((data.get("songs") or {}).get("results") or [])[:limit]
out = []
for song in songs:
    artists = song.get("artists") or []
    out.append({
        "id": song.get("videoId"),
        "title": song.get("title"),
        "artist": ", ".join(item.get("name") for item in artists if item.get("name")),
        "page_url": f"https://music.youtube.com/watch?v={song.get('videoId')}" if song.get("videoId") else "",
        "thumbnail_url": ((song.get("thumbnails") or [{}])[-1].get("url")),
    })
print(json.dumps(out, ensure_ascii=False))
"""
    result = run_subprocess([str(python_bin), "-c", script, query, str(limit)], timeout=40)
    if result.returncode != 0 or not result.stdout.strip():
        return []
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    tracks: List[Track] = []
    for index, item in enumerate(payload):
        video_id = item.get("id")
        page_url = item.get("page_url") or ""
        title = item.get("title") or ""
        if not video_id or not title or "watch?v=" not in page_url:
            continue
        tracks.append(
            Track(
                id=video_id,
                title=title,
                artist=clean_artist_name(item.get("artist") or ""),
                source="youtube",
                page_url=page_url,
                thumbnail_url=item.get("thumbnail_url"),
                rank_score=max(0.0, 3.0 - (index * 0.05)),
            )
        )
    return tracks[:limit]
