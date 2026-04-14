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

    def test_ai_variant_rank_below_official_version(self):
        resolver = Resolver()
        ai_variant = Track(
            id="ai",
            title="【那天下雨了】AI周杰倫 +5key版—年輕音色",
            artist="周杰倫影片製作",
            source="youtube",
            page_url="ai",
            duration_sec=224,
        )
        official = Track(
            id="official",
            title="那天下雨了 Official Audio",
            artist="周杰倫",
            source="youtube",
            page_url="official",
            duration_sec=223,
        )
        ai_score = resolver._score_track(ai_variant, "周杰倫 那天下雨了").rank_score
        official_score = resolver._score_track(official, "周杰倫 那天下雨了").rank_score
        self.assertGreater(official_score, ai_score)

    def test_wrong_song_title_rank_below_target_song(self):
        resolver = Resolver()
        wrong_song = Track(
            id="wrong",
            title="Jay Chou 周杰倫【Gold Rush Town 淘金小鎮】Official Music Video",
            artist="周杰倫 Jay Chou",
            source="youtube",
            page_url="wrong",
            duration_sec=215,
        )
        target_song = Track(
            id="target",
            title="那天下雨了 Official Audio",
            artist="周杰倫",
            source="youtube",
            page_url="target",
            duration_sec=223,
        )
        wrong_score = resolver._score_track(wrong_song, "周杰倫 那天下雨了").rank_score
        target_score = resolver._score_track(target_song, "周杰倫 那天下雨了").rank_score
        self.assertGreater(target_score, wrong_score)

    def test_anonymous_reuploader_rank_below_artist_channel(self):
        resolver = Resolver()
        reuploader = Track(
            id="reup",
            title="JAY CHOU周杰倫 新專輯 【太陽之子】- 03 那天下雨了",
            artist="abbw8776",
            source="youtube",
            page_url="reup",
            duration_sec=223,
        )
        artist_channel = Track(
            id="artist",
            title="那天下雨了 Official Audio",
            artist="周杰倫",
            source="youtube",
            page_url="artist",
            duration_sec=223,
        )
        reup_score = resolver._score_track(reuploader, "周杰倫 那天下雨了").rank_score
        artist_score = resolver._score_track(artist_channel, "周杰倫 那天下雨了").rank_score
        self.assertGreater(artist_score, reup_score)


if __name__ == "__main__":
    unittest.main()
