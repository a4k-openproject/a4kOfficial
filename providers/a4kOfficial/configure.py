# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

import importlib

import xbmcaddon
import xbmcgui

from resources.lib.modules.providers.install_manager import ProviderInstallManager

from providerModules.a4kOfficial import common
from providerModules.a4kOfficial.common import ADDON_IDS


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


def get_initial_provider_status(scraper=None):
    status = check_for_addon(ADDON_IDS[scraper]["plugin"])
    return (scraper, status)


def change_provider_status(scraper=None, status="enabled"):
    ProviderInstallManager().flip_provider_status('a4kOfficial', scraper, status)


def fix_provider_status(scraper=None):
    status = check_for_addon(scraper)

    common.log(
        "a4kOfficial: '{}' is{} installed; {}abling '{}'".format(
            ADDON_IDS[scraper]["plugin"],
            '' if status else ' not',
            'en' if status else 'dis',
            scraper,
        ),
        'info',
    )

    change_provider_status(scraper, "{}abled".format("en" if status else "dis"))

    return (scraper, status)


if common.get_setting("general.firstrun") == "true":
    common.set_setting("general.firstrun", "false")
    dialog = xbmcgui.Dialog()
    automatic = [get_initial_provider_status(scraper) for scraper in ADDON_IDS]

    choices = dialog.multiselect(
        "a4kOfficial: Choose providers to enable",
        [ADDON_IDS[i[0]]["name"] for i in automatic],
        preselect=[i for i in range(len(automatic)) if automatic[i][1]],
    )

    for i in range(len(automatic)):
        scraper, status = automatic[i][:2]
        if i in choices:
            provider = importlib.import_module(scraper)
            if hasattr(provider, "setup"):
                if dialog.yesno(
                    "a4kOfficial",
                    "Do you want to enable and setup {}?".format(
                        ADDON_IDS[scraper]["name"]
                    ),
                ):
                    success = provider.setup()
                    change_provider_status(
                        scraper, "{}abled".format("en" if success else "dis")
                    )
            else:
                change_provider_status(scraper, "enabled")
        else:
            change_provider_status(scraper, "disabled")
