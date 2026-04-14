from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from typing import List

from shared.lang import LANGS


class KKBoxHotChart:
    base_url = "https://kma.kkbox.com/charts/api/v1"

    def _fetch_json(self, path: str, query: dict) -> dict:
        request = Request(
            f"{self.base_url}{path}?{urlencode(query)}",
            headers={"User-Agent": "music-agent/0.1"},
        )
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))

    def get_categories(self) -> list:
        payload = self._fetch_json("/weekly/categories", {"terr": "tw", "lang": "tc", "type": "song"})
        return payload.get("data", [])

    def get_hot_tracks(self, lang_key: str, limit: int) -> List[dict]:
        category_id = LANGS[lang_key]["kkbox_category_id"]
        payload = self._fetch_json(
            "/weekly",
            {"terr": "tw", "lang": "tc", "type": "song", "cate": category_id},
        )
        songs = payload.get("data", {}).get("charts", {}).get("song", [])
        return songs[:limit]

