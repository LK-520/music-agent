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
from shared.runtime import MPV_SOCKET_PATH, ensure_runtime_dir


class MpvPlayer:
    def __init__(self) -> None:
        self.process: Optional[subprocess.Popen] = None

    def ensure_started(self) -> None:
        if shutil.which("mpv") is None:
            raise MusicError("PLAYER_UNAVAILABLE", "未检测到 mpv，请先安装 mpv")
        ensure_runtime_dir()
        if self.process and self.process.poll() is None and MPV_SOCKET_PATH.exists():
            return
        if MPV_SOCKET_PATH.exists():
            MPV_SOCKET_PATH.unlink()
        command = [
            "mpv",
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

