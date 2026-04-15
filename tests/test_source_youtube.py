import unittest
from unittest.mock import patch

from musicd.source_youtube import YouTubeAdapter
from shared.models import Track


class YouTubeAdapterTests(unittest.TestCase):
    def test_artist_only_query_prefers_artist_top_tracks(self):
        adapter = YouTubeAdapter()
        top_track = Track(
            id="7HYcDejCQcc",
            title="唯一 - Only One",
            artist="G.E.M.",
            source="youtube",
            page_url="https://music.youtube.com/watch?v=7HYcDejCQcc",
        )
        with patch("musicd.source_youtube.search_artist_top_tracks", return_value=[top_track]) as artist_mock:
            tracks = adapter.search("邓紫棋", 5)
        artist_mock.assert_called_once_with("邓紫棋", 5)
        self.assertEqual([track.title for track in tracks], ["唯一 - Only One"])

    def test_song_query_does_not_use_artist_top_tracks(self):
        adapter = YouTubeAdapter()
        with patch("musicd.source_youtube.search_artist_top_tracks") as artist_mock:
            with patch("musicd.source_youtube.get_yt_dlp_command", return_value=None):
                tracks = adapter.search("多远都要在一起 邓紫棋", 5)
        artist_mock.assert_not_called()
        self.assertEqual(tracks, [])


if __name__ == "__main__":
    unittest.main()
