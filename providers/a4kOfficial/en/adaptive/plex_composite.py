# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

from urllib.parse import quote

from providerModules.a4kOfficial.core.plex import PlexCore


class sources(PlexCore):
    def __init__(self):
        super(sources, self).__init__()

        self._base_url = f"plugin://{self._plugin}"
        self._movie_url = f"{self._base_url}" + "/?mode=5&url={base_url}{movie_id}"
        self._episode_url = f"{self._base_url}" + "/?mode=5&url={base_url}{episode_id}"

    def episode(self, simple_info, all_info, **kwargs):
        return super(PlexCore, self).episode(
            simple_info, all_info, single=False, **kwargs
        )

    def movie(self, simple_info, all_info, **kwargs):
        return super(PlexCore, self).movie(
            simple_info, all_info, single=False, **kwargs
        )

    def _make_source(self, item, url, **kwargs):
        source = super(sources, self)._make_source(item, url, **kwargs)

        source.update(
            {"url": kwargs["base_url"].format(**{k: quote(v) for k, v in url.items()})}
        )

        return source
