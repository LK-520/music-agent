import unittest

from shared.source import normalize_source


class SourceTests(unittest.TestCase):
    def test_normalize_source_aliases(self):
        self.assertEqual(normalize_source("y"), "youtube")
        self.assertEqual(normalize_source("youtube music"), "youtube")
        self.assertEqual(normalize_source("b"), "bilibili")
        self.assertEqual(normalize_source("sc"), "soundcloud")


if __name__ == "__main__":
    unittest.main()
