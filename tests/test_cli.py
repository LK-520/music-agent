import unittest
from unittest.mock import patch

from musicctl.cli import _should_follow_playback, build_payload, parse_args


class CliTests(unittest.TestCase):
    def test_hot_with_lang_payload(self):
        args = parse_args(["hot", "english"])
        payload = build_payload(args)
        self.assertEqual(payload, {"action": "hot", "lang": "english"})

    def test_volume_up_payload(self):
        args = parse_args(["volume", "up"])
        payload = build_payload(args)
        self.assertEqual(payload, {"action": "volume_up"})

    def test_doctor_payload(self):
        args = parse_args(["doctor", "--fix"])
        payload = build_payload(args)
        self.assertEqual(payload, {"action": "doctor", "fix": True})

    def test_state_payload(self):
        args = parse_args(["state", "hermes"])
        payload = build_payload(args)
        self.assertEqual(payload, {"action": "state", "target": "hermes"})

    def test_source_payload(self):
        args = parse_args(["source", "b"])
        payload = build_payload(args)
        self.assertEqual(payload, {"action": "source", "value": "b"})

    @patch("musicctl.cli.sys.stdout.isatty", return_value=True)
    @patch("musicctl.cli.sys.stdin.isatty", return_value=True)
    def test_interactive_play_defaults_to_follow(self, _stdin_mock, _stdout_mock):
        args = parse_args(["play", "后会无期"])
        self.assertTrue(_should_follow_playback(args))

    @patch("musicctl.cli.sys.stdout.isatty", return_value=True)
    @patch("musicctl.cli.sys.stdin.isatty", return_value=True)
    def test_detach_disables_interactive_follow(self, _stdin_mock, _stdout_mock):
        args = parse_args(["--detach", "play", "后会无期"])
        self.assertFalse(_should_follow_playback(args))

    @patch("musicctl.cli.sys.stdout.isatty", return_value=False)
    @patch("musicctl.cli.sys.stdin.isatty", return_value=False)
    def test_non_interactive_play_does_not_follow_without_flag(self, _stdin_mock, _stdout_mock):
        args = parse_args(["play", "后会无期"])
        self.assertFalse(_should_follow_playback(args))


if __name__ == "__main__":
    unittest.main()
