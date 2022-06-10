# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import xbmcaddon

from resources.lib.modules.providers.install_manager import ProviderInstallManager

from providerModules.a4kOfficial import common
from providers.a4kOfficial.en.adaptive import ADDON_IDS

for provider in ADDON_IDS:
    status = "enabled"
    try:
        xbmcaddon.Addon(ADDON_IDS[provider])
        status = "enabled"
    except Exception as e:
        common.log(e, 'info')
        common.log(
            "a4kOfficial: '{}' is not installed; disabling '{}'".format(
                ADDON_IDS[provider], provider
            ),
            'info',
        )
        status = "disabled"

    ProviderInstallManager().flip_provider_status('a4kOfficial', provider, status)
