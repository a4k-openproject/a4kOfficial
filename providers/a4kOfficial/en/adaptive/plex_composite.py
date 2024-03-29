# -*- coding: utf-8 -*-
from urllib.parse import quote

from providerModules.a4kOfficial.core.plex import PlexCore


class sources(PlexCore):
    def __init__(self):
        super().__init__()

        self._base_url = f"plugin://{self._plugin}"
        self._movie_url = f"{self._base_url}" + "/?mode=5&url={base_url}{movie_id}"
        self._episode_url = f"{self._base_url}" + "/?mode=5&url={base_url}{episode_id}"

    def episode(self, simple_info, info, **kwargs):
        return super().episode(simple_info, info, single=False, **kwargs)

    def movie(self, title, year, imdb, simple_info, info, **kwargs):
        return super().movie(title, year, imdb, simple_info, info, single=False, **kwargs)

    def _make_source(self, item, url, simple_info, info, **kwargs):
        source = super()._make_source(item, url, simple_info, info, **kwargs)

        source.update({"url": kwargs["base_url"].format(**{k: quote(v) for k, v in url.items()})})

        return source
