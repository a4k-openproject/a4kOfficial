# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

import re

from providerModules.a4kOfficial import common
from providerModules.a4kOfficial.core.justwatch import JustWatchCore


class sources(JustWatchCore):
    def __init__(self):
        super(sources, self).__init__()
        self._providers = ["pmp"]
        self._scheme = "standard_web"
        self._movie_url = "plugin://{}/?_=play&video_id={}"
        self._episode_url = "plugin://{}/?_=play&video_id={}"

    def _get_service_id(self, item, season=0, episode=0):
        if not self._service_offers:
            return None

        offer = self._service_offers[0]
        url = offer["urls"][self._scheme]
        if not common.check_url(url):
            return None

        id = (
            url.split("?")[0].split("/")[-1]
            if item["object_type"] == "movie"
            else re.findall("/video/(.+?)/", url)[0]
        )

        return id
