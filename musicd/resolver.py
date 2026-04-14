from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import Dict, Iterable, List, Sequence, Tuple

from musicd.hotlist_kkbox import KKBoxHotChart
from musicd.source_bilibili import BilibiliAdapter
from musicd.source_soundcloud import SoundCloudAdapter
from musicd.source_youtube import YouTubeAdapter
from shared.errors import MusicError
from shared.models import Queue, Track
from shared.utils import (
    clean_artist_name,
    matches_negative_term,
    normalize_title,
    query_tokens,
)


class Resolver:
    def __init__(self) -> None:
        self.adapters = {
            "youtube": YouTubeAdapter(),
            "bilibili": BilibiliAdapter(),
            "soundcloud": SoundCloudAdapter(),
        }
        self.hot_chart = KKBoxHotChart()
        self.platform_weight = {
            "youtube": 0.40,
            "bilibili": 0.20,
            "soundcloud": 0.10,
        }

    def build_keyword_queue(self, query: str, lang_key: str = "mandarin", limit: int = 20) -> Queue:
        selected = self._search_keyword_tracks(query=query, limit=limit)
        if not selected:
            raise MusicError("NO_RESULTS", f"未找到与“{query}”相关的可播放歌曲")
        tracks = self._resolve_tracks(selected)
        if not tracks:
            raise MusicError("SOURCE_RESOLVE_FAILED", "音源解析失败，请稍后重试")
        return Queue(
            source_type="keyword",
            source_query=query,
            items=tracks,
            current_index=1,
            total=len(tracks),
            lang=lang_key,
        )

    def build_hot_queue(self, lang_key: str, limit: int = 20) -> Queue:
        hot_items = self.hot_chart.get_hot_tracks(lang_key, max(limit * 2, 40))
        selected: List[Track] = []
        for item in hot_items:
            artist = clean_artist_name(item.get("artist_name") or item.get("artist_roles") or "")
            title = item.get("song_name") or ""
            candidates = self._search_keyword_tracks(f"{artist} {title}".strip(), limit=1)
            if candidates:
                candidate = candidates[0]
                candidate.rank_score += 1.0 - (len(selected) * 0.01)
                selected.append(candidate)
            if len(selected) >= limit:
                break
        tracks = self._resolve_tracks(selected[:limit])
        if not tracks:
            raise MusicError("NO_RESULTS", "热门榜单暂时可用，但没有匹配到可播放音源")
        return Queue(
            source_type="hot",
            source_query=lang_key,
            items=tracks,
            current_index=1,
            total=len(tracks),
            lang=lang_key,
        )

    def refresh_stream(self, track: Track) -> Track:
        adapter = self.adapters[track.source]
        track.stream_url = adapter.resolve_stream(track)
        track.resolved_at = time.time()
        return track

    def _search_keyword_tracks(self, query: str, limit: int) -> List[Track]:
        all_candidates: List[Track] = []
        search_limit = max(limit * 2, 20)
        source_names = ("youtube", "bilibili", "soundcloud")
        with ThreadPoolExecutor(max_workers=len(source_names)) as executor:
            future_map = {
                executor.submit(self.adapters[source_name].search, query, search_limit): source_name
                for source_name in source_names
            }
            for future in as_completed(future_map):
                try:
                    raw_tracks = future.result() or []
                except Exception:
                    continue
                filtered = [track for track in raw_tracks if self._is_track_allowed(track)]
                scored = [self._score_track(track, query) for track in filtered]
                all_candidates.extend(scored)
        deduped = self._dedupe(all_candidates)
        ranked = sorted(deduped, key=lambda item: item.rank_score, reverse=True)
        return ranked[:limit]

    def _resolve_tracks(self, tracks: Sequence[Track]) -> List[Track]:
        if not tracks:
            return []
        resolved_by_index: Dict[int, Track] = {}
        max_workers = min(6, len(tracks))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(self.refresh_stream, track): index
                for index, track in enumerate(tracks)
            }
            for future in as_completed(future_map):
                index = future_map[future]
                try:
                    resolved_by_index[index] = future.result()
                except Exception:
                    continue
        return [resolved_by_index[index] for index in sorted(resolved_by_index)]

    def _is_track_allowed(self, track: Track) -> bool:
        title = track.title or ""
        if matches_negative_term(title):
            return False
        if track.duration_sec is not None:
            if track.duration_sec < 30 or track.duration_sec > 900:
                return False
        normalized = normalize_title(title)
        if not normalized:
            return False
        return True

    def _score_track(self, track: Track, query: str) -> Track:
        title = normalize_title(track.title)
        artist = normalize_title(track.artist)
        score = self.platform_weight.get(track.source, 0.0)
        tokens = query_tokens(query)
        if title == normalize_title(query):
            score += 0.8
        matched = sum(1 for token in tokens if token in title or token in artist)
        if tokens:
            score += matched / len(tokens)
        artist_matched = sum(1 for token in tokens if token in artist)
        if artist_matched:
            score += 0.15 * artist_matched
        if track.duration_sec is not None:
            if 120 <= track.duration_sec <= 360:
                score += 0.2
            elif 30 <= track.duration_sec < 120:
                score -= 0.1
            elif 360 < track.duration_sec <= 900:
                score -= 0.05
        if "official" in title or "原唱" in title or "music video" in title:
            score += 0.2
        penalty_terms = {
            "remix": 0.3,
            "cover": 0.18,
            "歌词": 0.12,
            "lyric": 0.12,
            "合集": 0.4,
            "串烧": 0.35,
            "纯享": 0.15,
            "伴奏": 0.4,
            "dj": 0.2,
        }
        for term, penalty in penalty_terms.items():
            if term in title:
                score -= penalty
        track.rank_score = round(score, 4)
        return track

    def _dedupe(self, tracks: Iterable[Track]) -> List[Track]:
        result: List[Track] = []
        seen_exact: set = set()
        seen_fuzzy: Dict[Tuple[str, str], str] = {}
        for track in tracks:
            exact_key = (track.source, track.id)
            if exact_key in seen_exact:
                continue
            fuzzy_key = (normalize_title(track.title), normalize_title(track.artist))
            if fuzzy_key in seen_fuzzy and seen_fuzzy[fuzzy_key] == track.source:
                continue
            seen_exact.add(exact_key)
            seen_fuzzy[fuzzy_key] = track.source
            result.append(track)
        return result
