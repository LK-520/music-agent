from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterable


HERMES_CLI_PATH = Path.home() / ".hermes" / "hermes-agent" / "cli.py"
PATCH_MARKER = "music-agent Hermes state bar patch"

HERMES_PATCH_BLOCK = f"""
    # BEGIN {PATCH_MARKER}
    def _load_music_agent_status_snapshot(self) -> dict:
        cache = getattr(self, "_music_agent_status_cache", None) or {{}}
        now = time.monotonic()
        if cache and (now - float(cache.get("at", 0.0))) < 0.75:
            data = cache.get("data")
            return data if isinstance(data, dict) else {{}}
        status_path = Path.home() / ".cache" / "music-agent" / "status.json"
        data = {{}}
        try:
            if status_path.exists():
                with open(status_path, "r", encoding="utf-8") as handle:
                    loaded = json.load(handle)
                if isinstance(loaded, dict):
                    data = loaded
        except Exception:
            data = {{}}
        self._music_agent_status_cache = {{"at": now, "data": data}}
        return data

    def _music_agent_status_visible(self) -> bool:
        snapshot = self._load_music_agent_status_snapshot()
        return snapshot.get("state") in {{"playing", "paused"}}

    def _get_music_agent_status_fragments(self):
        snapshot = self._load_music_agent_status_snapshot()
        if snapshot.get("state") not in {{"playing", "paused"}}:
            return []
        width = self._get_tui_terminal_width()
        track = snapshot.get("track") or {{}}
        next_track = snapshot.get("next_track") or {{}}
        current = f"{{track.get('artist', '未知歌手')}} - {{track.get('title', '未知歌曲')}}"
        upcoming = (
            f"{{next_track.get('artist', '未知歌手')}} - {{next_track.get('title', '未知歌曲')}}"
            if next_track else "无"
        )
        state_label = "已暂停" if snapshot.get("state") == "paused" else "正在播放"
        if width < 76:
            text = current
        else:
            text = f"{{state_label}}: {{current}} │ 下一首: {{upcoming}}"
        text = self._trim_status_bar_text(text, max(8, width - 4))
        return [
            ("class:status-bar", " ♪ "),
            ("class:status-bar-strong", text),
            ("class:status-bar", " "),
        ]

    def _get_music_agent_tui_widgets(self) -> list:
        def _get_music_status():
            return self._get_music_agent_status_fragments()

        return [
            ConditionalContainer(
                Window(
                    content=FormattedTextControl(_get_music_status),
                    height=1,
                    wrap_lines=False,
                ),
                filter=Condition(lambda: self._music_agent_status_visible()),
            )
        ]
    # END {PATCH_MARKER}
"""


def _dedupe_paths(paths: Iterable[Path]) -> list[Path]:
    result: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        result.append(path)
    return result


def _is_patchable_hermes_cli(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return False
    return "class HermesCLI:" in text and "def _get_extra_tui_widgets(self) -> list:" in text


def _candidate_home_cli_paths() -> list[Path]:
    candidates = [HERMES_CLI_PATH]
    for env_key in ("APPDATA", "LOCALAPPDATA"):
        value = os.environ.get(env_key)
        if value:
            base = Path(value)
            candidates.append(base / "hermes" / "hermes-agent" / "cli.py")
            candidates.append(base / ".hermes" / "hermes-agent" / "cli.py")
    home = Path.home()
    candidates.extend(
        [
            home / "AppData" / "Roaming" / "hermes" / "hermes-agent" / "cli.py",
            home / "AppData" / "Roaming" / ".hermes" / "hermes-agent" / "cli.py",
            home / "AppData" / "Local" / "hermes" / "hermes-agent" / "cli.py",
            home / "AppData" / "Local" / ".hermes" / "hermes-agent" / "cli.py",
        ]
    )
    return _dedupe_paths(candidates)


def _candidate_launcher_paths() -> list[Path]:
    launchers: list[Path] = []
    for name in ("hermes", "hermes.exe", "hermes.cmd", "hermes-script.py"):
        resolved = shutil.which(name)
        if resolved:
            launchers.append(Path(resolved))
    return _dedupe_paths(launchers)


def _candidate_cli_paths_from_launcher(launcher_path: Path) -> list[Path]:
    candidates: list[Path] = []
    for base in (launcher_path, launcher_path.resolve()):
        try:
            ancestors = [base.parent, *base.parents]
        except Exception:
            ancestors = [base.parent]
        for ancestor in ancestors[:8]:
            candidates.extend(
                [
                    ancestor / "cli.py",
                    ancestor / "hermes-agent" / "cli.py",
                    ancestor.parent / "cli.py",
                ]
            )
    return _dedupe_paths(candidates)


def _candidate_python_bins_from_launcher(launcher_path: Path) -> list[Path]:
    candidates: list[Path] = []
    for base in (launcher_path, launcher_path.resolve()):
        name = base.name.lower()
        if name.endswith(".py") or name == "hermes":
            try:
                first_line = base.read_text(encoding="utf-8").splitlines()[0]
            except Exception:
                first_line = ""
            if first_line.startswith("#!"):
                shebang = first_line[2:].strip().split()[0]
                if shebang:
                    candidates.append(Path(shebang))
        parent = base.parent
        candidates.extend(
            [
                parent / "python",
                parent / "python3",
                parent / "python.exe",
                parent / "pythonw.exe",
            ]
        )
    return _dedupe_paths([path for path in candidates if path.exists()])


def _discover_cli_via_python(python_bin: Path) -> list[Path]:
    script = r"""
from pathlib import Path
import hermes_cli.main
results = []
try:
    import cli
    candidate = Path(cli.__file__).resolve()
    if candidate.exists():
        results.append(candidate)
except Exception:
    pass
main_path = Path(hermes_cli.main.__file__).resolve()
for ancestor in [main_path.parent, *main_path.parents[:6]]:
    for candidate in (
        ancestor / "cli.py",
        ancestor.parent / "cli.py",
        ancestor / "hermes-agent" / "cli.py",
    ):
        if candidate.exists():
            results.append(candidate.resolve())
seen = set()
for item in results:
    text = str(item)
    if text in seen:
        continue
    seen.add(text)
    print(text)
"""
    try:
        result = subprocess.run(
            [str(python_bin), "-c", script],
            capture_output=True,
            text=True,
            check=False,
            timeout=8,
        )
    except Exception:
        return []
    if result.returncode != 0:
        return []
    candidates: list[Path] = []
    for line in result.stdout.splitlines():
        text = line.strip()
        if text:
            candidates.append(Path(text))
    return _dedupe_paths(candidates)


def discover_hermes_cli_path(target_path: Path | None = None) -> Path:
    if target_path:
        target = target_path.expanduser()
        if _is_patchable_hermes_cli(target):
            return target
        raise FileNotFoundError(f"未找到可打补丁的 Hermes CLI 源码：{target}")

    candidates: list[Path] = []
    candidates.extend(_candidate_home_cli_paths())
    launchers = _candidate_launcher_paths()
    for launcher in launchers:
        candidates.extend(_candidate_cli_paths_from_launcher(launcher))
        for python_bin in _candidate_python_bins_from_launcher(launcher):
            candidates.extend(_discover_cli_via_python(python_bin))
    for candidate in _dedupe_paths(candidates):
        if _is_patchable_hermes_cli(candidate):
            return candidate
    raise FileNotFoundError("未自动找到 Hermes CLI 源码，请确认 Hermes 已安装，或手动指定 cli.py 路径")


def apply_hermes_statebar_patch(target_path: Path | None = None) -> str:
    target = discover_hermes_cli_path(target_path)

    source = target.read_text(encoding="utf-8")
    if PATCH_MARKER in source:
        begin_marker = f"    # BEGIN {PATCH_MARKER}"
        end_marker = f"    # END {PATCH_MARKER}"
        begin_index = source.find(begin_marker)
        end_index = source.find(end_marker)
        if begin_index == -1 or end_index == -1:
            raise RuntimeError("Hermes 状态栏补丁标记不完整，请手动检查 cli.py")
        end_index += len(end_marker)
        source = source[:begin_index] + HERMES_PATCH_BLOCK.rstrip() + source[end_index:]
        target.write_text(source, encoding="utf-8")
        return f"Hermes 状态栏音乐补丁已更新：{target}"

    method_anchor = "    def _get_extra_tui_widgets(self) -> list:\n"
    method_start = source.find(method_anchor)
    if method_start == -1:
        raise RuntimeError("未找到 HermesCLI._get_extra_tui_widgets，无法安装状态栏补丁")

    register_anchor = "\n    def _register_extra_tui_keybindings"
    method_end = source.find(register_anchor, method_start)
    if method_end == -1:
        raise RuntimeError("未找到 HermesCLI._register_extra_tui_keybindings，无法安装状态栏补丁")

    method_block = source[method_start:method_end]
    if "return self._get_music_agent_tui_widgets()" not in method_block:
        if "        return []" not in method_block:
            raise RuntimeError("HermesCLI._get_extra_tui_widgets 结构已变化，请手动检查")
        method_block = method_block.replace("        return []", "        return self._get_music_agent_tui_widgets()", 1)

    patched = source[:method_start] + HERMES_PATCH_BLOCK + "\n" + method_block + source[method_end:]
    backup = target.with_suffix(target.suffix + ".music-agent.bak")
    backup.write_text(source, encoding="utf-8")
    target.write_text(patched, encoding="utf-8")
    return f"Hermes 状态栏音乐补丁已安装：{target}（已备份到 {backup}）"
