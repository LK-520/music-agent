import unittest

from shared.models import Queue, Track


class ModelTests(unittest.TestCase):
    def test_queue_uses_one_based_index(self):
        queue = Queue(
            source_type="keyword",
            source_query="稻香",
            items=[Track(id="1", title="稻香", artist="周杰伦", source="youtube", page_url="x")],
            current_index=1,
            total=1,
        )
        self.assertEqual(queue.current_index, 1)


if __name__ == "__main__":
    unittest.main()

