# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

PACKAGE_NAME = "a4kOfficial"
ADDON_IDS = {
    "iplayer": {
        "plugin": "plugin.video.iplayerwww",
        "name": "BBC iPlayer",
        "type": "adaptive",
    },
    "curiositystream": {
        "plugin": "slyguy.curiositystream",
        "name": "CuriosityStream",
        "type": "adaptive",
    },
    "disneyplus": {
        "plugin": "slyguy.disney.plus",
        "name": "Disney+",
        "type": "adaptive",
    },
    "hbomax": {"plugin": "slyguy.hbo.max", "name": "HBO Max", "type": "adaptive"},
    "hulu": {"plugin": "slyguy.hulu", "name": "Hulu", "type": "adaptive"},
    "library": {"plugin": None, "name": "Library", "type": "direct"},
    "netflix": {
        "plugin": "plugin.video.netflix",
        "name": "Netflix",
        "type": "adaptive",
    },
    "paramountplus": {
        "plugin": "slyguy.paramount.plus",
        "name": "Paramount+",
        "type": "adaptive",
    },
    "plex": {
        "plugin": "plugin.video.composite_for_plex",
        "name": "Plex (Composite)",
        "type": "adaptive",
    },
    "primevideo": {
        "plugin": "plugin.video.amazon-test",
        "name": "Prime Video",
        "type": "adaptive",
    },
}
