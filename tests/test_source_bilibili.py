import unittest

from musicd.source_bilibili import BilibiliAdapter


class BilibiliAdapterTests(unittest.TestCase):
    def test_search_webpage_parses_bilibili_all_results(self):
        adapter = BilibiliAdapter()
        sample = r'''
        __pinia=(function(){return {searchResponse:{searchAllResponse:{result:[
        {result_type:"video",data:[{type:"video",bvid:"BV19qXQBYEh2",title:"［无损音质］《\u003Cem class=\"keyword\"\u003E那天下雨了\u003C\u002Fem\u003E》 周杰伦",author:"每天都开心的k",duration:"3:45",pic:"\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002Fc88cf0201889b1d78a95aa7b3dd89a15976ad7a3.jpg"}]}}]}}})()
        '''
        tracks = []
        for match in adapter._RESULT_PATTERN.finditer(sample):
            tracks.append(
                (
                    match.group("bvid"),
                    adapter._decode_js_string(match.group("title")),
                    adapter._decode_js_string(match.group("author")),
                    adapter._decode_js_string(match.group("duration")),
                    adapter._normalize_thumbnail_url(adapter._decode_js_string(match.group("pic"))),
                )
            )
        self.assertEqual(len(tracks), 1)
        bvid, title, author, duration, thumbnail = tracks[0]
        self.assertEqual(bvid, "BV19qXQBYEh2")
        self.assertIn("那天下雨了", title)
        self.assertEqual(author, "每天都开心的k")
        self.assertEqual(duration, "3:45")
        self.assertEqual(thumbnail, "https://i0.hdslb.com/bfs/archive/c88cf0201889b1d78a95aa7b3dd89a15976ad7a3.jpg")


if __name__ == "__main__":
    unittest.main()
