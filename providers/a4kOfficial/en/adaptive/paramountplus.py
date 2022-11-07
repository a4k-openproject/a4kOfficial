# -*- coding: utf-8 -*-
import re

from providerModules.a4kOfficial import common
from providerModules.a4kOfficial.core.justwatch import JustWatchCore


class sources(JustWatchCore):
    def __init__(self):
        super(sources, self).__init__(providers=["pmp"])

        self._movie_url = f"{self._movie_url.format(movie_url='/?_=play&video_id={movie_id}')}"
        self._episode_url = f"{self._episode_url.format(episode_url='/?_=play&video_id={episode_id}')}"

    def _get_service_id(self, item, season=0, episode=0):
        if not self._service_offers:
            return None

        offer = self._service_offers[0]
        url = offer["urls"][self._scheme]
        if not common.check_url(url):
            return None

        id = url.split("?")[0].split("/")[-1] if item["object_type"] == "movie" else re.findall("/video/(.+?)/", url)[0]

        return id
