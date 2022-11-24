# -*- coding: utf-8 -*-
import json
import re
import requests
from urllib.parse import quote_plus

from providerModules.a4kOfficial import common
from providerModules.a4kOfficial.core.justwatch import JustWatchCore


class sources(JustWatchCore):
    def __init__(self):
        super().__init__(providers=["bbc"])

        self._movie_url = (
            f"{self._movie_url.format(movie_url='/?mode=202&name=null&url={movie_id}&iconimage=null&description=null')}"
        )
        self._episode_url = f"{self._episode_url.format(episode_url='/?mode=202&name=null&url={episode_id}&iconimage=null&description=null')}"

    def _make_source(self, item, ids, simple_info, all_info, **kwargs):
        source = self._make_source(item, ids, simple_info, all_info, **kwargs)

        base_url = kwargs["base_url"]
        source["url"] = base_url.format(**({k: quote_plus(v) for k, v in ids.items()}))

    def _get_service_id(self, item, season=0, episode=0):
        if not self._service_offers:
            return None

        offer = self._service_offers[0]
        url = offer["urls"][self._scheme]
        if not common.check_url(url):
            return None

        return self._get_service_ep_id(url, item, season, episode) if "/episodes/" in url else url

    def _get_service_ep_id(self, show_id, item, season, episode):
        seriesId = None
        series_split = show_id.split("seriesId=")
        if type(series_split == list) and len(series_split) > 1:
            seriesId = show_id.split("seriesId=")[1]

        r = requests.get(show_id, timeout=10).text
        eps = re.findall("__IPLAYER_REDUX_STATE__\s*=\s*({.+?});</script>", r)
        if eps:
            eps = json.loads(eps[0])

        if seriesId:
            seasons = eps.get("header", {}).get("availableSlices", {})
            series_id = [s.get("id", "") for s in seasons if int(re.sub("[^0-9]", "", s["title"])) == season]
            if series_id:
                series_id = series_id[0]

            if not series_id == seriesId:
                show_id = show_id.replace(seriesId, series_id)
                r = requests.get(show_id, timeout=10).text
                eps = re.findall("__IPLAYER_REDUX_STATE__\s*=\s*({.+?});</script>", r)
                if eps:
                    eps = json.loads(eps[0])

        eps = eps.get("entities", {})
        eps = [e.get("props", {}).get("href", "") for e in eps]
        ep = [e for e in eps if re.compile(rf"series-{season}-{episode}-").findall(e)]
        if ep:
            ep = ep[0]
        ep = "https://www.bbc.co.uk" + ep if not ep.startswith("http") else ep

        return None if not common.check_url(ep) else {"episode_id": ep}
