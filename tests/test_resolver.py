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


if __name__ == "__main__":
    unittest.main()

