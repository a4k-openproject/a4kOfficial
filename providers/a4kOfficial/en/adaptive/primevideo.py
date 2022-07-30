# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

from providerModules.a4kOfficial.core_justwatch import JustWatchCore


class sources(JustWatchCore):
    def __init__(self):
        super(sources, self).__init__()
        self._providers = ['amp', 'amz']
        self._scheme = "standard_web"
        self._movie_url = "plugin://{}/?asin={}&mode=PlayVideo&name=None&adult=0&trailer=0&selbitrate=0"
        self._episode_url = "plugin://{}/?asin={}&mode=PlayVideo&name=None&adult=0&trailer=0&selbitrate=0"

    def _get_service_id(self, item, season=0, episode=0):
        if not self._current_offers:
            return None

        offer = self._current_offers[0]
        url = offer['urls'][self._scheme]
        id = url.rstrip('/').split('gti=')[1]

        return id