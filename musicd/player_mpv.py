from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import time
from pathlib import Path
from typing import Any, Optional

from shared.errors import MusicError
from shared.runtime import MPV_PID_PATH, MPV_SOCKET_PATH, ensure_runtime_dir
from shared.utils import run_subprocess


class MpvPlayer:
    def __init__(self) -> None:
        self.process: Optional[subprocess.Popen] = None

    def _mpv_path(self) -> Optional[str]:
        for candidate in [shutil.which("mpv"), "/usr/local/bin/mpv", "/opt/homebrew/bin/mpv"]:
            if candidate and Path(candidate).exists():
                return candidate
        return None

    def _process_alive(self, pid: int) -> bool:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    def _cleanup_orphan_mpv(self) -> None:
        if MPV_PID_PATH.exists():
            try:
                pid = int(MPV_PID_PATH.read_text(encoding="utf-8").strip())
                if self._process_alive(pid):
                    run_subprocess(["kill", "-TERM", str(pid)], timeout=10)
                    time.sleep(0.2)
                MPV_PID_PATH.unlink(missing_ok=True)
            except Exception:
                MPV_PID_PATH.unlink(missing_ok=True)
        socket_path = str(MPV_SOCKET_PATH)
        run_subprocess(["pkill", "-f", f"--input-ipc-server={socket_path}"], timeout=10)
        if MPV_SOCKET_PATH.exists():
            MPV_SOCKET_PATH.unlink()

    def ensure_started(self) -> None:
        mpv_path = self._mpv_path()
        if mpv_path is None:
            raise MusicError("PLAYER_UNAVAILABLE", "未检测到 mpv，请先安装 mpv")
        ensure_runtime_dir()
        if MPV_PID_PATH.exists():
            try:
                pid = int(MPV_PID_PATH.read_text(encoding="utf-8").strip())
                if self._process_alive(pid) and MPV_SOCKET_PATH.exists():
                    return
            except Exception:
                pass
        if self.process and self.process.poll() is None and MPV_SOCKET_PATH.exists():
            MPV_PID_PATH.write_text(str(self.process.pid), encoding="utf-8")
            return
        self._cleanup_orphan_mpv()
        command = [
            mpv_path,
            "--idle=yes",
            "--no-video",
            "--force-window=no",
            "--keep-open=no",
            f"--input-ipc-server={MPV_SOCKET_PATH}",
            "--really-quiet",
        ]
        self.process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
        MPV_PID_PATH.write_text(str(self.process.pid), encoding="utf-8")
        deadline = time.time() + 10
        while time.time() < deadline:
            if MPV_SOCKET_PATH.exists():
                return
            time.sleep(0.1)
        raise MusicError("PLAYER_UNAVAILABLE", "mpv 已启动，但 IPC 未就绪")

    def _send(self, command: list) -> dict:
        self.ensure_started()
        payload = {"command": command, "request_id": int(time.time() * 1000) % 1_000_000}
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(10)
            client.connect(str(MPV_SOCKET_PATH))
            client.sendall((json.dumps(payload) + "\n").encode("utf-8"))
            chunks = []
            while True:
                data = client.recv(65536)
                if not data:
                    break
                chunks.append(data)
                if b"\n" in data:
                    break
        raw = b"".join(chunks).split(b"\n", 1)[0].decode("utf-8")
        return json.loads(raw) if raw else {}

    def load(self, url: str) -> None:
        response = self._send(["loadfile", url, "replace"])
        if response.get("error") not in (None, "success"):
            raise MusicError("PLAYER_UNAVAILABLE", "播放器加载失败")

    def stop(self) -> None:
        self._send(["stop"])

    def quit(self) -> None:
        if MPV_SOCKET_PATH.exists():
            try:
                self._send(["quit"])
            except Exception:
                pass
        if MPV_PID_PATH.exists():
            try:
                pid = int(MPV_PID_PATH.read_text(encoding="utf-8").strip())
                if self._process_alive(pid):
                    run_subprocess(["kill", "-TERM", str(pid)], timeout=10)
            except Exception:
                pass
        MPV_PID_PATH.unlink(missing_ok=True)
        if MPV_SOCKET_PATH.exists():
            MPV_SOCKET_PATH.unlink()

    def set_pause(self, value: bool) -> None:
        self._send(["set_property", "pause", value])

    def set_volume(self, value: int) -> None:
        self._send(["set_property", "volume", value])

    def get_property(self, name: str, default: Any = None) -> Any:
        response = self._send(["get_property", name])
        if response.get("error") not in (None, "success"):
            return default
        return response.get("data", default)

    def is_idle(self) -> bool:
        return bool(self.get_property("idle-active", True))
