# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

from providerModules.a4kOfficial.core.plex import PlexCore


class sources(PlexCore):
    def __init__(self):
        super(sources, self).__init__()
        
        self._movie_url = (
            f"{self._movie_url.format(movie_url='/?mode=5&url={movie_id}')}"
        )
        self._episode_url = (
            f"{self._episode_url.format(episode_url='/?mode=6&url={episode_id}')}"
        )