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

    def test_command_appends_status_snapshot(self):
        text = format_response(
            {
                "ok": True,
                "action": "mute",
                "status_snapshot": {
                    "state": "playing",
                    "track": {"artist": "周杰伦", "title": "稻香", "source": "youtube"},
                    "next_track": {"artist": "周杰伦", "title": "七里香"},
                    "volume": 0,
                    "muted": True,
                    "queue_index": 1,
                    "queue_total": 20,
                    "lang": "mandarin",
                    "source_preference": "youtube",
                },
            }
        )
        self.assertIn("已静音", text)
        self.assertIn("当前播放：周杰伦 - 稻香", text)
        self.assertIn("音源偏好：YouTube Music", text)


if __name__ == "__main__":
    unittest.main()
