# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

import xbmcaddon

from resources.lib.modules.providers.install_manager import ProviderInstallManager

from providerModules.a4kOfficial import common
from providerModules.a4kOfficial.common import ADDON_IDS


def fix_provider_status(scraper=None, plugin=None):
    status = True
    try:
        xbmcaddon.Addon(plugin)
    except RuntimeError:
        status = False

    common.log(
        "a4kOfficial: '{}' is{} installed; {}abling '{}'".format(
            plugin,
            '' if status else ' not',
            'en' if status else 'dis',
            scraper,
        ),
        'info',
    )
    ProviderInstallManager().flip_provider_status(
        'a4kOfficial', scraper, "enabled" if status else "disabled"
    )


if common.get_setting("general.firstrun") == "true":
    for scraper, plugin in ADDON_IDS.items():
        fix_provider_status(scraper, plugin)
    common.set_setting("general.firstrun", "false")
