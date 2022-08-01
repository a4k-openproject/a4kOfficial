# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

from providerModules.a4kOfficial import common
from providerModules.a4kOfficial.core_plex import Plex, PlexCore

_api = Plex()


def setup():
    success = _api.auth()
    for setting in ["plex.token", "plex.client_id", "plex.device_id"]:
        common.log(common.get_setting(setting))

    return success


class sources(PlexCore):
    def __init__(self):
        super(sources, self).__init__()
        self._movie_url = "plugin://{}/?url={}&mode=5"
