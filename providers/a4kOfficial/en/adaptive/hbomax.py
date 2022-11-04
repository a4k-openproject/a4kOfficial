# -*- coding: utf-8 -*-
from providerModules.a4kOfficial.core.justwatch import JustWatchCore


class sources(JustWatchCore):
    def __init__(self):
        super(sources, self).__init__(providers=["hmf", "hba", "hbm"])

        self._movie_url = f"{self._movie_url.format(movie_url='/?_=play&slug={movie_id}')}"
        self._episode_url = f"{self._episode_url.format(episode_url='/?_=play&slug={episode_id}')}"
