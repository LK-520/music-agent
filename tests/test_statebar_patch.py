import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from shared.statebar_patch import (
    PATCH_MARKER,
    _candidate_cli_paths_from_launcher,
    apply_hermes_statebar_patch,
    discover_hermes_cli_path,
)


SAMPLE_HERMES_CLI = """class HermesCLI:
    def _get_extra_tui_widgets(self) -> list:
        \"\"\"Return extra prompt_toolkit widgets to insert into the TUI layout.

        Wrapper CLIs can override this to inject widgets (e.g. a mini-player,
        overlay menu) into the layout without overriding ``run()``.  Widgets
        are inserted between the spacer and the status bar.
        \"\"\"
        return []

    def _register_extra_tui_keybindings(self, kb, *, input_area) -> None:
        pass
"""


class StatebarPatchTests(unittest.TestCase):
    def test_apply_hermes_patch_inserts_music_widget_block(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "cli.py"
            target.write_text(SAMPLE_HERMES_CLI, encoding="utf-8")

            message = apply_hermes_statebar_patch(target)
            patched = target.read_text(encoding="utf-8")

        self.assertIn("已安装", message)
        self.assertIn(PATCH_MARKER, patched)
        self.assertIn("return self._get_music_agent_tui_widgets()", patched)
        self.assertIn("_get_music_agent_status_fragments", patched)

    def test_apply_hermes_patch_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "cli.py"
            target.write_text(SAMPLE_HERMES_CLI, encoding="utf-8")

            apply_hermes_statebar_patch(target)
            message = apply_hermes_statebar_patch(target)

        self.assertIn("已更新", message)

    def test_launcher_candidate_search_supports_unix_and_windows_layouts(self):
        unix_candidates = _candidate_cli_paths_from_launcher(Path("/tmp/hermes-agent/venv/bin/hermes"))
        windows_candidates = _candidate_cli_paths_from_launcher(Path("C:/Hermes/hermes-agent/venv/Scripts/hermes.exe"))

        self.assertIn(Path("/tmp/hermes-agent/cli.py"), unix_candidates)
        self.assertIn(Path("C:/Hermes/hermes-agent/cli.py"), windows_candidates)

    def test_discover_hermes_cli_path_uses_launcher_ancestors(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "hermes-agent"
            launcher = root / "venv" / "bin" / "hermes"
            target = root / "cli.py"
            launcher.parent.mkdir(parents=True, exist_ok=True)
            launcher.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
            target.write_text(SAMPLE_HERMES_CLI, encoding="utf-8")

            with patch("shared.statebar_patch._candidate_home_cli_paths", return_value=[]):
                with patch("shared.statebar_patch._candidate_launcher_paths", return_value=[launcher]):
                    with patch("shared.statebar_patch._candidate_python_bins_from_launcher", return_value=[]):
                        discovered = discover_hermes_cli_path()

        self.assertEqual(discovered, target)


if __name__ == "__main__":
    unittest.main()
