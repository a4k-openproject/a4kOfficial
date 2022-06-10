import os
import re

from resources.lib.common import provider_tools
from resources.lib.modules.globals import g

from providerModules.a4kOfficial import dom_parser

PACKAGE_NAME = 'a4kOfficial'
ADDON_IDS = {
    "amazonprime": "plugin.video.amazon-test",
    "disneyplus": "slyguy.disney.plus",
    "hulu": "slyguy.hulu",
    "netflix": "plugin.video.netflix",
    "hbomax": "slyguy.hbo.max",
    "paramountplus": "slyguy.paramount.plus",
    "curiositystream": "slyguy.curiositystream",
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
        attrs = dict(
            (key, re.compile(value + ('$' if value else '')))
            for key, value in attrs.items()
        )
    results = dom_parser.parse_dom(html, name, attrs, ret)

    if ret:
        results = [result.attrs[ret.lower()] for result in results]
    else:
        results = [result.content for result in results]

    return results
