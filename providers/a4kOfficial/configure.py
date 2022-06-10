# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import xbmcaddon

from resources.lib.modules.providers.install_manager import ProviderInstallManager

from providerModules.a4kOfficial import common
from providerModules.a4kOfficial.common import ADDON_IDS

for provider in ADDON_IDS:
    status = True
    try:
        xbmcaddon.Addon(ADDON_IDS[provider])
    except Exception:
        status = False

    common.log(
        "a4kOfficial: '{}' is{} installed; {}abling '{}'".format(
            ADDON_IDS[provider],
            '' if status else ' not',
            'en' if status else 'dis',
            provider,
        ),
        'info',
    )
    ProviderInstallManager().flip_provider_status(
        'a4kOfficial', provider, "enabled" if status else "disabled"
    )
