import unittest

from musicd.resolver import Resolver
from shared.models import Track


class ResolverTests(unittest.TestCase):
    def test_dedupe_keeps_cross_platform_versions(self):
        resolver = Resolver()
        tracks = [
            Track(id="a", title="稻香", artist="周杰伦", source="youtube", page_url="1"),
            Track(id="b", title="稻香", artist="周杰伦", source="bilibili", page_url="2"),
            Track(id="a", title="稻香", artist="周杰伦", source="youtube", page_url="1"),
        ]
        deduped = resolver._dedupe(tracks)
        self.assertEqual(len(deduped), 2)

    def test_original_artist_and_official_rank_above_fan_upload(self):
        resolver = Resolver()
        fan_upload = Track(
            id="fan",
            title="Cat Pure - Jay Chou 周杰倫【03那天下雨了】 新專輯 Music Video",
            artist="Cat Pure",
            source="youtube",
            page_url="fan",
            duration_sec=223,
        )
        official = Track(
            id="official",
            title="那天下雨了 Official Audio",
            artist="周杰倫",
            source="youtube",
            page_url="official",
            duration_sec=223,
        )
        fan_score = resolver._score_track(fan_upload, "周杰倫 那天下雨了").rank_score
        official_score = resolver._score_track(official, "周杰倫 那天下雨了").rank_score
        self.assertGreater(official_score, fan_score)


if __name__ == "__main__":
    unittest.main()
