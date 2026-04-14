from __future__ import annotations

import html
import json
from urllib.parse import quote
from typing import List

from musicd.source_base import SourceAdapter
from shared.models import Track
from shared.utils import clean_artist_name, duration_to_seconds, run_subprocess


class BilibiliAdapter(SourceAdapter):
    source_name = "bilibili"

    def search(self, query: str, limit: int) -> List[Track]:
        per_page = 20
        pages = max(1, (limit + per_page - 1) // per_page)
        tracks: List[Track] = []
        for page in range(1, pages + 1):
            url = (
                "https://api.bilibili.com/x/web-interface/search/type"
                f"?search_type=video&keyword={quote(query)}&page={page}"
            )
            response = run_subprocess(
                [
                    "curl",
                    "-sL",
                    url,
                    "-H",
                    "User-Agent: Mozilla/5.0",
                    "-H",
                    "Referer: https://www.bilibili.com",
                    "-H",
                    "Origin: https://www.bilibili.com",
                ],
                timeout=30,
            )
            if response.returncode != 0 or not response.stdout.strip():
                continue
            try:
                payload = json.loads(response.stdout)
            except json.JSONDecodeError:
                continue
            if payload.get("code") not in (None, 0):
                continue
            for item in payload.get("data", {}).get("result", []):
                bvid = item.get("bvid")
                if not bvid:
                    continue
                title = html.unescape(item.get("title", ""))
                title = title.replace('<em class="keyword">', "").replace("</em>", "")
                tracks.append(
                    Track(
                        id=bvid,
                        title=title,
                        artist=clean_artist_name(item.get("author") or ""),
                        source=self.source_name,
                        page_url=f"https://www.bilibili.com/video/{bvid}",
                        duration_sec=duration_to_seconds(item.get("duration") or ""),
                        thumbnail_url=item.get("pic"),
                    )
                )
                if len(tracks) >= limit:
                    return tracks
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
            raise RuntimeError(result.stderr.strip() or "bilibili resolve failed")
        payload = json.loads(result.stdout)
        formats = payload.get("formats") or []
        audio_formats = [
            item for item in formats if item.get("url") and item.get("vcodec") == "none"
        ]
        best = audio_formats[-1] if audio_formats else {}
        stream_url = best.get("url") or payload.get("url")
        if not stream_url:
            raise RuntimeError("no playable bilibili stream")
        track.duration_sec = payload.get("duration") or track.duration_sec
        track.thumbnail_url = payload.get("thumbnail") or track.thumbnail_url
        track.artist = clean_artist_name(payload.get("uploader") or track.artist)
        track.title = payload.get("title") or track.title
        return stream_url
