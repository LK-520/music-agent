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

    def test_doctor_message(self):
        text = format_response(
            {
                "ok": False,
                "action": "doctor",
                "checks": [
                    {"ok": True, "message": "已检测到 mpv：/usr/local/bin/mpv"},
                    {"ok": False, "message": "未检测到可用的 yt-dlp"},
                ],
                "fix_notes": ["无法自动安装 yt-dlp，请手动执行：python3 -m pip install --user yt-dlp"],
            }
        )
        self.assertIn("环境检查结果", text)
        self.assertIn("FAIL 未检测到可用的 yt-dlp", text)


if __name__ == "__main__":
    unittest.main()
