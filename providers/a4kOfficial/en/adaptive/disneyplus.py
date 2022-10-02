# -*- coding: utf-8 -*-
from providerModules.a4kOfficial.core.justwatch import JustWatchCore


class sources(JustWatchCore):
    def __init__(self):
        super(sources, self).__init__(providers=["dnp"], scheme="deeplink_web")

        self._movie_url = f"{self._movie_url.format(movie_url='/?_=play&_play=1&content_id={movie_id}')}"
        self._episode_url = f"{self._episode_url.format(episode_url='/?_=play&_play=1&content_id={episode_id}')}"
