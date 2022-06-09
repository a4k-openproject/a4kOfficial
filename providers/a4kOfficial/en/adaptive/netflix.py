# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

from providerModules.a4kOfficial.core import Core


class sources(Core):
    def __init__(self):
        super(sources, self).__init__()
        self._providers = ["nfx", "nff", "nfk"]
        self._scraper = "netflix"
        self._service = "netflix"
        self._movie_url = "plugin://plugin.video.netflix/play_strm/{}/"
        self._episode_url = "plugin://plugin.video.netflix/play_strm/{}/"
