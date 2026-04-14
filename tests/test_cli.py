import unittest

from musicctl.cli import build_payload, parse_args


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


if __name__ == "__main__":
    unittest.main()
