# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

from providerModules.a4kOfficial.core import Core


class DisneyPlus(Core):
    def __init__(self):
        super(self, DisneyPlus).__init__()
        self._providers = ["dnp"]
        self._scraper = "disneyplus"
        self._service = "disneyplus"
        self._scheme = "deeplink_web"
        self._movie_url = "plugin://slyguy.disney.plus/?_=play&_play=1&content_id={}"
        self._episode_url = "plugin://slyguy.disney.plus/?_=play&_play=1&content_id={}"

    def _get_service_ep_id(self, show_id, season, episode, item):
        return self._get_service_id(item=item)
