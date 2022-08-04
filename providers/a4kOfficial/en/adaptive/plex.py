# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

from providerModules.a4kOfficial.core.plex import PlexCore


class sources(PlexCore):
    def __init__(self):
        super(sources, self).__init__()
        self._movie_url = "plugin://{}/?url={}&mode=5"
        self._episode_url = "plugin://{}/?url={}&mode=6"
