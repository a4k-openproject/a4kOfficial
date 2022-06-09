# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

from providerModules.a4kOfficial.core import Core


class sources(Core):
    def __init__(self):
        super(sources, self).__init__()
        self._providers = ["hlu"]
        self._scraper = "hulu"
        self._service = "hulu"
        self._movie_url = "plugin://slyguy.hulu/?_=play&id={}"
        self._episode_url = "plugin://slyguy.hulu/?_=play&id={}"

    def _get_service_ep_id(self, show_id, season, episode, item):
        return self._get_service_id(item=item)
