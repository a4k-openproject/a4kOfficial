# -*- coding: utf-8 -*-
PACKAGE_NAME = "a4kOfficial"
REPO_ADDRESS = "https://github.com/a4k-openproject/repository.a4kOfficial/raw/master/repo/zips/repository.a4kOfficial/repository.a4kOfficial-1.0.zip"
REPO_ID = "repository.a4kOfficial"

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
    "hbomax": {
        "plugin": "slyguy.hbo.max",
        "name": "HBO Max",
        "type": "adaptive",
        "settings": {
            "DD": "ac3_enabled",
            "DD+": "ec3_enabled",
            "ATMOS": "atmos_enabled",
            "HEVC": "h265",
            "4K": "4k_enabled",
            "DV": "dolby_vision",
        },
    },
    "hulu": {
        "plugin": "slyguy.hulu",
        "name": "Hulu",
        "type": "adaptive",
        "settings": {
            "DD+": "ec3",
            "HEVC": "h265",
            "4K": "4k",
        },
    },
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
        "settings": {
            "DD": "ac3_enabled",
            "DD+": "ec3_enabled",
            "ATMOS": "atmos_enabled",
            "HEVC": "h265",
            "4K": "4k_enabled",
            "DV": "dolby_vision",
        },
    },
    "plex_composite": {
        "plugin": "plugin.video.composite_for_plex",
        "name": "Plex (Composite)",
        "type": "adaptive",
    },
    "plex_direct": {"plugin": None, "name": "Plex (Direct)", "type": "direct"},
    "primevideo": {
        "plugin": "plugin.video.amazon-test",
        "name": "Prime Video",
        "type": "adaptive",
    },
}
