# -*- coding: utf-8 -*-
import re
import requests

from providerModules.a4kOfficial import common
from providerModules.a4kOfficial.core.justwatch import JustWatchCore


INSTANT_WATCHER_COUNTRIES = {
    "AR": "21",
    "AU": "23",
    "BE": "26",
    "BR": "29",
    "CA": "33",
    "CO": "36",
    "CZ": "307",
    "FR": "45",
    "DE": "39",
    "GR": "327",
    "HK": "331",
    "HU": "334",
    "IS": "265",
    "IN": "337",
    "IL": "336",
    "IT": "269",
    "JP": "267",
    "LT": "357",
    "MY": "378",
    "MX": "65",
    "NL": "67",
    "PL": "392",
    "PT": "268",
    "RU": "402",
    "SG": "408",
    "SK": "412",
    "ZA": "447",
    "KR": "348",
    "ES": "270",
    "SE": "73",
    "CH": "34",
    "TH": "425",
    "TR": "432",
    "GB": "46",
    "US": "78",
}


class sources(JustWatchCore):
    def __init__(self):
        super().__init__(providers=["nfx", "nfk"])

        self._movie_url = f"{self._movie_url.format(movie_url='/play/movie/{movie_id}/')}"
        self._episode_url = (
            f"{self._episode_url.format(episode_url='/play/show/{show_id}/season/{season_id}/episode/{episode_id}')}"
        )

    def _get_service_ep_id(self, show_id, item, season, episode):
        code = INSTANT_WATCHER_COUNTRIES.get(self._country, "78")
        url = f"https://www.instantwatcher.com/netflix/{code}/title/{show_id}"
        r = requests.get(url, timeout=10).text

        r = common.parseDOM(r, "div", attrs={"class": "tdChildren-titles"})[0]
        seasons = re.findall(
            r'(<div class="iw-title netflix-title list-title".+?<div class="grandchildren-titles"></div></div>)',
            r,
            flags=re.I | re.S,
        )
        _season = [s for s in seasons if int(re.findall(r">Season (.+?)</a>", s, flags=re.I | re.S)[0]) == season][0]
        episodes = common.parseDOM(_season, "a", ret="data-title-id")
        episode_id = episodes[int(episode)]

        return (
            None
            if not common.check_url(f"https://www.netflix.com/watch/{episode_id}")
            else {"season_id": episodes[0], "episode_id": episode_id}
        )
