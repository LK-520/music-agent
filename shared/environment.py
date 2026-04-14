from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from shared.utils import run_subprocess


class EnvironmentIssue(RuntimeError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def _python_candidates() -> List[str]:
    candidates: List[str] = []
    for candidate in [
        sys.executable,
        shutil.which("python3"),
        "/usr/bin/python3",
        "/usr/local/bin/python3",
        "/opt/homebrew/bin/python3",
    ]:
        if candidate and candidate not in candidates and Path(candidate).exists():
            candidates.append(candidate)
    return candidates


def _yt_dlp_bin_candidates() -> List[str]:
    candidates: List[str] = []
    for candidate in [
        shutil.which("yt-dlp"),
        str(Path.home() / ".local" / "bin" / "yt-dlp"),
        str(Path.home() / "Library" / "Python" / "3.9" / "bin" / "yt-dlp"),
        str(Path.home() / "Library" / "Python" / "3.10" / "bin" / "yt-dlp"),
        str(Path.home() / "Library" / "Python" / "3.11" / "bin" / "yt-dlp"),
        str(Path.home() / "Library" / "Python" / "3.12" / "bin" / "yt-dlp"),
        str(Path.home() / "Library" / "Python" / "3.13" / "bin" / "yt-dlp"),
        str(Path.home() / "Library" / "Python" / "3.14" / "bin" / "yt-dlp"),
    ]:
        if candidate and candidate not in candidates and Path(candidate).exists():
            candidates.append(candidate)
    return candidates


def get_mpv_path() -> Optional[str]:
    for candidate in [
        shutil.which("mpv"),
        "/opt/homebrew/bin/mpv",
        "/usr/local/bin/mpv",
    ]:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def get_yt_dlp_command() -> Optional[List[str]]:
    for candidate in _yt_dlp_bin_candidates():
        result = run_subprocess([candidate, "--version"], timeout=20)
        if result.returncode == 0:
            return [candidate]
    for python_bin in _python_candidates():
        result = run_subprocess([python_bin, "-m", "yt_dlp", "--version"], timeout=20)
        if result.returncode == 0:
            return [python_bin, "-m", "yt_dlp"]
    return None


def _path_has_local_bin() -> bool:
    path_entries = os.environ.get("PATH", "").split(":")
    return str(Path.home() / ".local" / "bin") in path_entries


def collect_environment_report() -> dict:
    mpv_path = get_mpv_path()
    yt_dlp_command = get_yt_dlp_command()
    checks = [
        {
            "key": "mpv",
            "ok": bool(mpv_path),
            "message": f"已检测到 mpv：{mpv_path}" if mpv_path else "未检测到 mpv",
        },
        {
            "key": "yt_dlp",
            "ok": bool(yt_dlp_command),
            "message": (
                f"已检测到 yt-dlp：{' '.join(yt_dlp_command)}"
                if yt_dlp_command
                else "未检测到可用的 yt-dlp"
            ),
        },
        {
            "key": "local_bin",
            "ok": _path_has_local_bin(),
            "message": (
                "PATH 已包含 ~/.local/bin"
                if _path_has_local_bin()
                else "PATH 未包含 ~/.local/bin，终端里可能找不到 musicctl"
            ),
        },
    ]
    blocking_issues = [
        check["message"]
        for check in checks
        if check["key"] in {"mpv", "yt_dlp"} and not check["ok"]
    ]
    warnings = [
        check["message"]
        for check in checks
        if check["key"] not in {"mpv", "yt_dlp"} and not check["ok"]
    ]
    return {
        "ok": not blocking_issues,
        "checks": checks,
        "blocking_issues": blocking_issues,
        "warnings": warnings,
        "mpv_path": mpv_path,
        "yt_dlp_command": yt_dlp_command,
    }


def format_blocking_message(report: dict) -> str:
    parts = []
    if report["blocking_issues"]:
        parts.append("环境检查未通过：")
        parts.extend(report["blocking_issues"])
    if report["warnings"]:
        parts.append("附加提醒：")
        parts.extend(report["warnings"])
    parts.append("请先运行：musicctl --text doctor")
    return "；".join(parts)


def ensure_playback_environment() -> None:
    report = collect_environment_report()
    if not report["ok"]:
        raise EnvironmentIssue(format_blocking_message(report))


def _try_install_yt_dlp() -> str:
    for python_bin in _python_candidates():
        result = run_subprocess([python_bin, "-m", "pip", "--version"], timeout=20)
        if result.returncode != 0:
            continue
        install = run_subprocess([python_bin, "-m", "pip", "install", "--user", "yt-dlp"], timeout=300)
        if install.returncode == 0 and get_yt_dlp_command():
            return f"已尝试通过 {python_bin} 安装 yt-dlp"
    return "无法自动安装 yt-dlp，请手动执行：python3 -m pip install --user yt-dlp"


def _try_install_mpv() -> str:
    brew = shutil.which("brew")
    if not brew:
        return "未检测到 Homebrew，无法自动安装 mpv，请手动安装 mpv"
    install = run_subprocess([brew, "install", "mpv"], timeout=1800)
    if install.returncode == 0 and get_mpv_path():
        return "已尝试通过 Homebrew 安装 mpv"
    stderr = (install.stderr or "").strip()
    if stderr:
        return f"自动安装 mpv 失败：{stderr.splitlines()[-1]}"
    return "自动安装 mpv 失败，请检查 Homebrew 权限后重试"


def attempt_environment_fix() -> list[str]:
    notes: list[str] = []
    if not get_yt_dlp_command():
        notes.append(_try_install_yt_dlp())
    if not get_mpv_path():
        notes.append(_try_install_mpv())
    return notes

