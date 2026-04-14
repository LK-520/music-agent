from __future__ import annotations

import json
from typing import List

from musicd.source_base import SourceAdapter
from shared.models import Track
from shared.utils import clean_artist_name, run_subprocess


class YouTubeAdapter(SourceAdapter):
    source_name = "youtube"

    def search(self, query: str, limit: int) -> List[Track]:
        command = [
            "python3",
            "-m",
            "yt_dlp",
            "--flat-playlist",
            "--dump-single-json",
            f"ytsearch{limit}:{query}",
        ]
        result = run_subprocess(command, timeout=120)
        if result.returncode != 0 or not result.stdout.strip():
            return []
        payload = json.loads(result.stdout)
        tracks: List[Track] = []
        for entry in payload.get("entries", []):
            if entry.get("ie_key") != "Youtube":
                continue
            video_id = entry.get("id")
            if not video_id:
                continue
            tracks.append(
                Track(
                    id=video_id,
                    title=entry.get("title") or "",
                    artist=clean_artist_name(entry.get("channel") or entry.get("uploader") or ""),
                    source=self.source_name,
                    page_url=entry.get("url") or f"https://www.youtube.com/watch?v={video_id}",
                    thumbnail_url=(entry.get("thumbnails") or [{}])[-1].get("url"),
                )
            )
        return tracks

    def resolve_stream(self, track: Track) -> str:
        command = [
            "python3",
            "-m",
            "yt_dlp",
            "-f",
            "bestaudio/best",
            "--no-playlist",
            "-J",
            track.page_url,
        ]
        result = run_subprocess(command, timeout=120)
        if result.returncode != 0 or not result.stdout.strip():
            raise RuntimeError(result.stderr.strip() or "youtube resolve failed")
        payload = json.loads(result.stdout)
        formats = payload.get("formats") or []
        audio_formats = [
            item for item in formats if item.get("url") and item.get("vcodec") == "none"
        ]
        best = audio_formats[-1] if audio_formats else {}
        stream_url = best.get("url") or payload.get("url")
        if not stream_url:
            raise RuntimeError("no playable youtube stream")
        track.duration_sec = payload.get("duration") or track.duration_sec
        track.thumbnail_url = payload.get("thumbnail") or track.thumbnail_url
        track.artist = clean_artist_name(
            payload.get("artist") or payload.get("channel") or payload.get("uploader") or track.artist
        )
        track.title = payload.get("title") or track.title
        return stream_url

