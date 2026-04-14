from __future__ import annotations

import argparse
import fcntl
import json
import os
import signal
import socketserver
import sys
import threading
from pathlib import Path
from subprocess import Popen
from time import sleep, time

from musicd.state import PlaybackManager
from shared.errors import MusicError
from shared.runtime import LOCK_PATH, LOG_PATH, PID_PATH, SOCKET_PATH, ensure_runtime_dir
from shared.utils import json_dumps


MANAGER = PlaybackManager()
SERVER: ThreadedUnixServer | None = None


class RequestHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        raw = self.rfile.readline().decode("utf-8").strip()
        if not raw:
            return
        try:
            payload = json.loads(raw)
            response = dispatch(payload)
        except MusicError as exc:
            response = exc.to_dict()
        except Exception as exc:
            response = {
                "ok": False,
                "error_code": "INTERNAL_ERROR",
                "message": str(exc) or "内部错误",
            }
        try:
            self.wfile.write(json_dumps(response))
        except BrokenPipeError:
            # The CLI may have been interrupted while the server was still
            # preparing the queue. Treat that as a normal detached client.
            return


class ThreadedUnixServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True


def dispatch(payload: dict) -> dict:
    action = payload.get("action")
    if action == "play":
        return MANAGER.play_keyword(payload.get("query", ""))
    if action == "hot":
        return MANAGER.play_hot(payload.get("lang"))
    if action == "pause":
        return MANAGER.pause()
    if action == "resume":
        return MANAGER.resume()
    if action == "next":
        return MANAGER.next_track()
    if action == "prev":
        return MANAGER.prev_track()
    if action == "stop":
        return MANAGER.stop()
    if action == "shutdown":
        response = MANAGER.shutdown()
        if SERVER is not None:
            threading.Thread(target=SERVER.shutdown, daemon=True).start()
        return response
    if action == "status":
        return MANAGER.status()
    if action == "volume":
        return MANAGER.set_volume(int(payload["value"]))
    if action == "volume_up":
        return MANAGER.volume_up()
    if action == "volume_down":
        return MANAGER.volume_down()
    if action == "mute":
        return MANAGER.mute()
    if action == "unmute":
        return MANAGER.unmute()
    if action == "lang":
        return MANAGER.set_lang(payload.get("value"))
    raise MusicError("INVALID_ARGUMENT", f"不支持的命令：{action}")


def run_server() -> None:
    global SERVER
    ensure_runtime_dir()
    if SOCKET_PATH.exists():
        SOCKET_PATH.unlink()
    PID_PATH.write_text(str(os.getpid()), encoding="utf-8")
    MANAGER.start_monitor()
    try:
        with ThreadedUnixServer(str(SOCKET_PATH), RequestHandler) as server:
            SERVER = server
            server.serve_forever()
    finally:
        SERVER = None
        PID_PATH.unlink(missing_ok=True)
        if SOCKET_PATH.exists():
            SOCKET_PATH.unlink()


def daemonize() -> None:
    ensure_runtime_dir()
    with open(LOCK_PATH, "w", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        if SOCKET_PATH.exists():
            return
        if PID_PATH.exists():
            try:
                pid = int(PID_PATH.read_text(encoding="utf-8").strip())
                os.kill(pid, 0)
                deadline = time() + 5
                while time() < deadline:
                    if SOCKET_PATH.exists():
                        return
                    sleep(0.1)
            except Exception:
                try:
                    PID_PATH.unlink()
                except FileNotFoundError:
                    pass
        with open(LOG_PATH, "a", encoding="utf-8") as log_file, open(os.devnull, "rb") as null_in:
            Popen(
                [sys.executable, "-m", "musicd.daemon", "--serve"],
                stdout=log_file,
                stderr=log_file,
                stdin=null_in,
                start_new_session=True,
                cwd=str(Path(__file__).resolve().parents[1]),
            )
        deadline = time() + 10
        while time() < deadline:
            if SOCKET_PATH.exists():
                return
            sleep(0.1)
    raise MusicError("DAEMON_UNAVAILABLE", "musicd 启动失败，请查看日志")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true")
    args = parser.parse_args(argv)
    if args.serve:
        run_server()
        return 0
    daemonize()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
