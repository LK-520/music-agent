import unittest

from musicctl.formatter import format_response


class FormatterTests(unittest.TestCase):
    def test_hot_message(self):
        text = format_response(
            {
                "ok": True,
                "action": "hot",
                "lang": "english",
                "queue_total": 20,
                "track": {"artist": "Adele", "title": "Hello"},
            }
        )
        self.assertIn("英语热门歌曲队列", text)
        self.assertIn("Adele - Hello", text)


if __name__ == "__main__":
    unittest.main()

