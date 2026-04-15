#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.statebar_patch import apply_hermes_statebar_patch


def main() -> int:
    parser = argparse.ArgumentParser(prog="apply_statebar.py")
    parser.add_argument("target", choices=("hermes", "openclaw"))
    args = parser.parse_args()

    if args.target == "openclaw":
        print("OpenClaw 状态栏预留接口已保留，暂未实现。")
        return 1

    try:
        print(apply_hermes_statebar_patch())
        return 0
    except Exception as exc:
        print(f"安装 Hermes 状态栏音乐补丁失败：{exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
