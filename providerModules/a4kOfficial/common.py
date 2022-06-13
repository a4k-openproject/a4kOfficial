import xbmc

import math
import os

from resources.lib.common import provider_tools
from resources.lib.modules.globals import g

PACKAGE_NAME = 'a4kOfficial'
ADDON_IDS = {
    "amazonprime": "plugin.video.amazon-test",
    "disneyplus": "slyguy.disney.plus",
    "hulu": "slyguy.hulu",
    "netflix": "plugin.video.netflix",
    "hbomax": "slyguy.hbo.max",
    "paramountplus": "slyguy.paramount.plus",
    "curiositystream": "slyguy.curiositystream",
    "iplayer": "plugin.video.iplayerwww",
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
