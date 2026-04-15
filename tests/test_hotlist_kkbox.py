import unittest
from unittest.mock import patch

from musicd.hotlist_kkbox import KKBoxHotChart


class KKBoxHotChartTests(unittest.TestCase):
    def test_get_hot_tracks_uses_daily_api_with_current_date(self):
        chart = KKBoxHotChart()
        captured = {}

        def fake_fetch(path, query):
            captured["path"] = path
            captured["query"] = query
            return {"data": {"charts": {"song": [{"song_name": "测试歌曲"}]}}}

        with patch.object(chart, "_current_chart_date", return_value="2026-04-16"):
            with patch.object(chart, "_fetch_json", side_effect=fake_fetch):
                songs = chart.get_hot_tracks("mandarin", 20)

        self.assertEqual(captured["path"], "/daily")
        self.assertEqual(captured["query"]["category"], 297)
        self.assertEqual(captured["query"]["date"], "2026-04-16")
        self.assertEqual(captured["query"]["limit"], 20)
        self.assertNotIn("cate", captured["query"])
        self.assertEqual(len(songs), 1)

    def test_get_categories_uses_daily_categories(self):
        chart = KKBoxHotChart()
        with patch.object(chart, "_fetch_json", return_value={"data": [{"category_id": 297}]}) as fetch_mock:
            categories = chart.get_categories()

        fetch_mock.assert_called_once_with("/daily/categories", {"terr": "tw", "lang": "tc", "type": "song"})
        self.assertEqual(categories, [{"category_id": 297}])


if __name__ == "__main__":
    unittest.main()
