from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from musicd.daemon import daemonize
from musicd.ipc import send_request
from musicctl.formatter import format_response
from shared.runtime import SOCKET_PATH


def ensure_daemon() -> None:
    if SOCKET_PATH.exists():
        try:
            send_request({"action": "status"})
            return
        except Exception:
            try:
                SOCKET_PATH.unlink()
            except FileNotFoundError:
                pass
    daemonize()


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="musicctl")
    parser.add_argument("--text", action="store_true", help="输出中文文本而不是 JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)

    play_parser = subparsers.add_parser("play")
    play_parser.add_argument("query")

    hot_parser = subparsers.add_parser("hot")
    hot_parser.add_argument("lang", nargs="?")

    subparsers.add_parser("pause")
    subparsers.add_parser("resume")
    subparsers.add_parser("next")
    subparsers.add_parser("prev")
    subparsers.add_parser("stop")
    subparsers.add_parser("status")
    subparsers.add_parser("mute")
    subparsers.add_parser("unmute")

    volume_parser = subparsers.add_parser("volume")
    volume_parser.add_argument("value")

    lang_parser = subparsers.add_parser("lang")
    lang_parser.add_argument("value", nargs="?")

    return parser.parse_args(argv)


def build_payload(args: argparse.Namespace) -> dict:
    command = args.command
    if command == "play":
        return {"action": "play", "query": args.query}
    if command == "hot":
        return {"action": "hot", "lang": args.lang}
    if command == "pause":
        return {"action": "pause"}
    if command == "resume":
        return {"action": "resume"}
    if command == "next":
        return {"action": "next"}
    if command == "prev":
        return {"action": "prev"}
    if command == "stop":
        return {"action": "stop"}
    if command == "status":
        return {"action": "status"}
    if command == "mute":
        return {"action": "mute"}
    if command == "unmute":
        return {"action": "unmute"}
    if command == "lang":
        return {"action": "lang", "value": args.value}
    if command == "volume":
        if args.value == "up":
            return {"action": "volume_up"}
        if args.value == "down":
            return {"action": "volume_down"}
        return {"action": "volume", "value": int(args.value)}
    raise ValueError(f"Unsupported command: {command}")


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    ensure_daemon()
    response = send_request(build_payload(args))
    if args.text:
        print(format_response(response))
    else:
        print(json.dumps(response, ensure_ascii=False))
    return 0 if response.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
