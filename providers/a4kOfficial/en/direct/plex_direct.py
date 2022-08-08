# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

from providerModules.a4kOfficial import common
from providerModules.a4kOfficial.api.plex import Plex
from providerModules.a4kOfficial.core.plex import PlexCore

_api = Plex()


def setup():
    success = _api.auth()
    for setting in ["plex.token", "plex.client_id", "plex.device_id"]:
        common.log(common.get_setting(setting))

    return success


class sources(PlexCore):
    def __init__(self):
        super(sources, self).__init__()

        self._movie_url = "{base_url}{movie_id}" + f"&X-Plex-Token={self._token}"
        self._episode_url = "{base_url}{episode_id}" + f"&X-Plex-Token={self._token}"

    def episode(self, simple_info, all_info, **kwargs):
        return super(PlexCore, self).episode(
            simple_info, all_info, single=False, **kwargs
        )

    def movie(self, simple_info, all_info, **kwargs):
        return super(PlexCore, self).movie(
            simple_info, all_info, single=False, **kwargs
        )
