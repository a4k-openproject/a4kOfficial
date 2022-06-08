import os

from resources.lib.common import provider_tools
from resources.lib.modules.globals import g

PACKAGE_NAME = 'a4kOfficial'
API_KEY = "91359e7719e3103b8240c769f2e5e79b"


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
