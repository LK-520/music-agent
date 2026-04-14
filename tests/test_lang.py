import unittest

from shared.lang import normalize_lang


class LangTests(unittest.TestCase):
    def test_normalize_lang_aliases(self):
        self.assertEqual(normalize_lang("华语"), "mandarin")
        self.assertEqual(normalize_lang("english"), "english")
        self.assertEqual(normalize_lang("jp"), "japanese")
        self.assertEqual(normalize_lang("韩文"), "korean")
        self.assertEqual(normalize_lang("yue"), "cantonese")


if __name__ == "__main__":
    unittest.main()

