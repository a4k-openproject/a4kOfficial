# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

import xbmc
import xbmcaddon

import math
import os

from resources.lib.common import provider_tools
from resources.lib.modules.globals import g
from resources.lib.modules.providers.install_manager import ProviderInstallManager

PACKAGE_NAME = 'a4kOfficial'
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
        "name": "Plex",
        "type": "adaptive",
    },
    "primevideo": {
        "plugin": "plugin.video.amazon-test",
        "name": "Prime Video",
        "type": "adaptive",
    },
}


def log(msg, level='info'):
    g.log('{}'.format(msg), level)


def debug(msg, format=None):
    if format:
        msg.format(format)
    g.log(msg, 'debug')


def get_all_relative_py_files(file):
    files = os.listdir(os.path.dirname(file))
    return [
        filename[:-3]
        for filename in files
        if not filename.startswith('__') and filename.endswith('.py')
    ]


def get_setting(id):
    return provider_tools.get_setting(PACKAGE_NAME, id)


def set_setting(id, value):
    return provider_tools.set_setting(PACKAGE_NAME, id, value)


def parseDOM(html, name='', attrs=None, ret=False):
    if attrs:
        import re

        attrs = dict(
            (key, re.compile(value + ('$' if value else '')))
            for key, value in attrs.items()
        )
    from providerModules.a4kOfficial import dom_parser

    results = dom_parser.parse_dom(html, name, attrs, ret)

    if ret:
        results = [result.attrs[ret.lower()] for result in results]
    else:
        results = [result.content for result in results]

    return results


def execute_jsonrpc(method, params):
    import json

    call_params = {"id": 1, "jsonrpc": "2.0", "method": method, "params": params}
    call = json.dumps(call_params)
    response = xbmc.executeJSONRPC(call)
    return json.loads(response)


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "{}{}".format(s, size_name[i])


def get_kodi_version():
    return xbmc.getInfoLabel("System.BuildVersion")


def get_platform_system():
    from platform import system

    return system()


def get_platform_machine():
    from platform import machine

    return machine()


def check_for_addon(plugin):
    if plugin is None:
        return False

    status = True
    try:
        xbmcaddon.Addon(plugin)
    except RuntimeError:
        status = False
    finally:
        return status


def change_provider_status(scraper=None, status="enabled"):
    ProviderInstallManager().flip_provider_status('a4kOfficial', scraper, status)
