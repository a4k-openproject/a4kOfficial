# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

from providerModules.a4kOfficial import common
from providerModules.a4kOfficial.core.justwatch import JustWatchCore


class sources(JustWatchCore):
    def __init__(self):
        super(sources, self).__init__(providers=["amp", "amz", "prv"])

        self._movie_url = f"{self._movie_url.format(movie_url='/?mode=PlayVideo&name=None&adult=0&trailer=0&selbitrate=0&asin={movie_id}')}"
        self._episode_url = f"{self._episode_url.format(episode_url='/?mode=PlayVideo&name=None&adult=0&trailer=0&selbitrate=0&asin={episode_id}')}"

    def _get_service_id(self, item, season=0, episode=0):
        if not self._service_offers:
            return None

        offer = self._service_offers[0]
        url = offer["urls"][self._scheme]
        if not common.check_url(url):
            return None

        id = url.rstrip("/").split("gti=")[1]

        return id
