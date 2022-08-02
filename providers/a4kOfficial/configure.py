# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

import importlib

import xbmcgui

from providerModules.a4kOfficial import common, ADDON_IDS

from resources.lib.modules.globals import g


def _get_initial_provider_status(scraper=None):
    status = common.check_for_addon(ADDON_IDS[scraper]["plugin"])
    return (scraper, status)


if common.get_setting("general.firstrun") == "true":
    dialog = xbmcgui.Dialog()
    automatic = [_get_initial_provider_status(scraper) for scraper in ADDON_IDS]

    choices = dialog.multiselect(
        "a4kOfficial: Choose providers to enable",
        [ADDON_IDS[i[0]]["name"] for i in automatic],
        preselect=[i for i in range(len(automatic)) if automatic[i][1]],
    )

    for i in range(len(automatic)):
        scraper, status = automatic[i][:2]
        if i in choices:
            module = "providers.a4kOfficial.en.{}.{}".format(
                ADDON_IDS[scraper]["type"], scraper
            )
            provider = importlib.import_module(module)

            if hasattr(provider, "setup"):
                if dialog.yesno(
                    "a4kOfficial",
                    "Do you want to enable and setup {}?".format(
                        g.color_string(ADDON_IDS[scraper]["name"])
                    ),
                ):
                    success = provider.setup()
                    if not success:
                        common.log(
                            "a4kOfficial.{}: Setup not complete; disabling".format(
                                scraper
                            )
                        )
                    common.change_provider_status(
                        scraper, "{}abled".format("en" if success else "dis")
                    )
            else:
                common.change_provider_status(scraper, "enabled")
        else:
            common.change_provider_status(scraper, "disabled")

    common.set_setting("general.firstrun", "false")
