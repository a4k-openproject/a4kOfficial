# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

from providerModules.a4kOfficial import common


class AddonNotInstalledError(Exception):
    def __init__(self, scraper, plugin):
        common.log(
            'a4kOfficial.{}: {} not installed.'.format(scraper, plugin),
            'error',
        )
