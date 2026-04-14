from __future__ import annotations

import threading
import time
from typing import Optional

from musicd.player_mpv import MpvPlayer
from musicd.resolver import Resolver
from shared.errors import MusicError, invalid_argument
from shared.lang import DEFAULT_LANG, display_lang, normalize_lang
from shared.models import PlaybackState, Queue, Track


class PlaybackManager:
    def __init__(self) -> None:
        self.state = PlaybackState(lang_preference=DEFAULT_LANG)
        self.player = MpvPlayer()
        self.resolver = Resolver()
        self.lock = threading.RLock()
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_started = False
        self._consecutive_failures = 0
        self._last_time_pos = 0.0

    def start_monitor(self) -> None:
        if not self._monitor_started:
            self._monitor_started = True
            self._monitor_thread.start()

    def play_keyword(self, query: str) -> dict:
        if not query.strip():
            raise invalid_argument("关键词不能为空")
        self.player.ensure_started()
        queue = self.resolver.build_keyword_queue(query=query.strip(), lang_key=self.state.lang_preference)
        with self.lock:
            self._replace_queue(queue)
        return self._play_response("play", query)

    def play_hot(self, lang_override: Optional[str] = None) -> dict:
        lang_key = normalize_lang(lang_override) if lang_override else self.state.lang_preference
        if not lang_key:
            raise invalid_argument("不支持的语种，请输入 华语/英语/日语/韩语/粤语 或简易英文")
        self.player.ensure_started()
        queue = self.resolver.build_hot_queue(lang_key=lang_key)
        with self.lock:
            self._replace_queue(queue)
        return self._play_response("hot", display_lang(lang_key))

    def pause(self) -> dict:
        with self.lock:
            if self.state.state != "playing":
                raise MusicError("NOTHING_PLAYING", "当前没有正在播放的音乐")
            self.player.set_pause(True)
            self.state.state = "paused"
            return {"ok": True, "action": "pause"}

    def resume(self) -> dict:
        with self.lock:
            if self.state.state != "paused":
                raise MusicError("NOTHING_TO_RESUME", "当前没有可恢复的播放内容")
            self.player.set_pause(False)
            self.state.state = "playing"
            return {"ok": True, "action": "resume", "track": self.state.current_track.to_dict()}

    def next_track(self) -> dict:
        with self.lock:
            track = self._advance(1)
            return {"ok": True, "action": "next", "track": track.to_dict()}

    def prev_track(self) -> dict:
        with self.lock:
            track = self._advance(-1)
            return {"ok": True, "action": "prev", "track": track.to_dict()}

    def stop(self) -> dict:
        with self.lock:
            if self.state.queue:
                try:
                    self.player.stop()
                except Exception:
                    pass
            self.state.queue = None
            self.state.current_track = None
            self.state.state = "idle"
            self.state.error_code = None
            self.state.message = None
            return {"ok": True, "action": "stop"}

    def shutdown(self) -> dict:
        with self.lock:
            try:
                self.player.stop()
            except Exception:
                pass
            try:
                self.player.quit()
            except Exception:
                pass
            self.state.queue = None
            self.state.current_track = None
            self.state.state = "idle"
            self.state.error_code = None
            self.state.message = None
            return {"ok": True, "action": "shutdown"}

    def status(self) -> dict:
        with self.lock:
            queue_total = self.state.queue.total if self.state.queue else 0
            queue_index = self.state.queue.current_index if self.state.queue else None
            next_track = None
            elapsed_sec = None
            duration_sec = None
            if self.state.queue and self.state.queue.items and queue_index:
                next_index = (queue_index % len(self.state.queue.items))
                next_track = self.state.queue.items[next_index].to_dict()
            if self.state.state in {"playing", "paused"} and self.state.current_track:
                elapsed_sec = self.player.get_property("time-pos", 0) or 0
                duration_sec = self.player.get_property("duration", self.state.current_track.duration_sec)
            return {
                "ok": True,
                "action": "status",
                "state": self.state.state,
                "volume": self.state.volume,
                "muted": self.state.muted,
                "queue_total": queue_total,
                "queue_index": queue_index,
                "loop": True,
                "lang": self.state.lang_preference,
                "track": self.state.current_track.to_dict() if self.state.current_track else None,
                "next_track": next_track,
                "elapsed_sec": elapsed_sec,
                "duration_sec": duration_sec,
                "error_code": self.state.error_code,
                "message": self.state.message,
            }

    def set_volume(self, value: int) -> dict:
        if value < 0 or value > 100:
            raise invalid_argument("无效音量值，请输入 0 到 100")
        with self.lock:
            self.player.set_volume(value)
            self.state.volume = value
            if value > 0:
                self.state.last_nonzero_volume = value
            return {"ok": True, "action": "volume", "volume": value}

    def volume_up(self) -> dict:
        return self.set_volume(min(100, self.state.volume + 5))

    def volume_down(self) -> dict:
        return self.set_volume(max(0, self.state.volume - 5))

    def mute(self) -> dict:
        with self.lock:
            if self.state.volume > 0:
                self.state.last_nonzero_volume = self.state.volume
            self.player.set_volume(0)
            self.state.muted = True
            self.state.volume = 0
            return {"ok": True, "action": "mute"}

    def unmute(self) -> dict:
        with self.lock:
            volume = self.state.last_nonzero_volume or 50
            self.player.set_volume(volume)
            self.state.muted = False
            self.state.volume = volume
            return {"ok": True, "action": "unmute", "volume": volume}

    def set_lang(self, value: Optional[str]) -> dict:
        if not value:
            return {
                "ok": True,
                "action": "lang",
                "lang": self.state.lang_preference,
                "display": display_lang(self.state.lang_preference),
            }
        lang_key = normalize_lang(value)
        if not lang_key:
            raise invalid_argument("不支持的语种，请输入 华语/英语/日语/韩语/粤语 或简易英文")
        with self.lock:
            self.state.lang_preference = lang_key
        return {"ok": True, "action": "lang", "lang": lang_key, "display": display_lang(lang_key)}

    def _replace_queue(self, queue: Queue) -> None:
        self.state.queue = queue
        self._consecutive_failures = 0
        self._play_current()

    def _play_current(self) -> Track:
        queue = self.state.queue
        if not queue or not queue.items or not queue.current_index:
            raise MusicError("QUEUE_EMPTY", "当前没有正在播放的音乐")
        track = queue.items[queue.current_index - 1]
        if not track.stream_url or not track.resolved_at or time.time() - track.resolved_at > 900:
            track = self.resolver.refresh_stream(track)
            queue.items[queue.current_index - 1] = track
        self.player.load(track.stream_url)
        if self.state.muted:
            self.player.set_volume(0)
        else:
            self.player.set_volume(self.state.volume)
        self.player.set_pause(False)
        self._last_time_pos = 0.0
        self.state.current_track = track
        self.state.state = "playing"
        self.state.error_code = None
        self.state.message = None
        return track

    def _advance(self, step: int) -> Track:
        queue = self.state.queue
        if not queue or not queue.items or not queue.current_index:
            raise MusicError("NOTHING_PLAYING", "当前没有正在播放的音乐")
        total = len(queue.items)
        queue.current_index = ((queue.current_index - 1 + step) % total) + 1
        return self._play_current()

    def _handle_track_failure(self) -> None:
        with self.lock:
            if not self.state.queue or not self.state.queue.items:
                return
            self._consecutive_failures += 1
            if self._consecutive_failures >= min(3, len(self.state.queue.items)):
                self.state.state = "error"
                self.state.error_code = "SOURCE_RESOLVE_FAILED"
                self.state.message = "连续多首歌曲播放失败，请重新点播"
                return
            try:
                self._advance(1)
            except Exception:
                self.state.state = "error"
                self.state.error_code = "SOURCE_RESOLVE_FAILED"
                self.state.message = "音源解析失败，请稍后重试"

    def _handle_track_end(self) -> None:
        with self.lock:
            if not self.state.queue or not self.state.queue.items:
                return
            self._consecutive_failures = 0
            self._last_time_pos = 0.0
            try:
                self._advance(1)
            except Exception:
                self.state.state = "error"
                self.state.error_code = "SOURCE_RESOLVE_FAILED"
                self.state.message = "自动切歌失败，请稍后重试"

    def _play_response(self, action: str, query: str) -> dict:
        next_track = None
        if self.state.queue and self.state.queue.items and self.state.queue.current_index:
            next_index = self.state.queue.current_index % len(self.state.queue.items)
            next_track = self.state.queue.items[next_index].to_dict()
        return {
            "ok": True,
            "action": action,
            "query": query,
            "queue_total": self.state.queue.total if self.state.queue else 0,
            "queue_index": self.state.queue.current_index if self.state.queue else None,
            "loop": True,
            "lang": self.state.queue.lang if self.state.queue else self.state.lang_preference,
            "track": self.state.current_track.to_dict() if self.state.current_track else None,
            "next_track": next_track,
        }

    def _monitor_loop(self) -> None:
        while True:
            time.sleep(2)
            with self.lock:
                if self.state.state != "playing" or not self.state.queue or not self.state.current_track:
                    continue
                current_track = self.state.current_track
            try:
                if self.player.is_idle():
                    duration = current_track.duration_sec or 0
                    played_enough = self._last_time_pos >= 30
                    near_end = bool(duration and self._last_time_pos >= max(duration - 5, duration * 0.85))
                    if near_end or played_enough:
                        self._handle_track_end()
                    else:
                        self._handle_track_failure()
                else:
                    current_pos = self.player.get_property("time-pos", 0) or 0
                    self._last_time_pos = float(current_pos)
            except MusicError as exc:
                with self.lock:
                    self.state.state = "error"
                    self.state.error_code = exc.code
                    self.state.message = exc.message
