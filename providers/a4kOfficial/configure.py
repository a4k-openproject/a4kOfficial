# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

import importlib

import requests

import xbmcaddon
import xbmcgui

from providerModules.a4kOfficial import common, ADDON_IDS

from resources.lib.modules.globals import g
from resources.lib.modules.providers.install_manager import ProviderInstallManager

_ipify = "https://api.ipify.org?format=json"
_ipinfo = "https://ipinfo.io/{}/json"


def _get_current_ip():
    data = requests.get(_ipify)
    if data.ok:
        return data.json().get("ip", "0.0.0.0")


def _get_country_code():
    ip = _get_current_ip()
    data = requests.get(_ipinfo.format(ip))

    if data.ok:
        return data.json().get("country", "US")


def _get_initial_provider_status(scraper=None):
    status = check_for_addon(ADDON_IDS[scraper]["plugin"])
    return (scraper, status)


def change_provider_status(scraper=None, status="enabled"):
    ProviderInstallManager().flip_provider_status("a4kOfficial", scraper, status)


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


if common.get_setting("general.firstrun") == "true":
    common.set_setting("justwatch.country", _get_country_code() or "US")

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
            module = f"providers.a4kOfficial.en.{ADDON_IDS[scraper]['type']}.{scraper}"
            provider = importlib.import_module(module)

            if hasattr(provider, "setup"):
                if dialog.yesno(
                    "a4kOfficial",
                    f"Do you want to enable and setup {g.color_string(ADDON_IDS[scraper]['name'])}?",
                ):
                    success = provider.setup()
                    if not success:
                        common.log(
                            f"a4kOfficial.{scraper}: Setup not complete; disabling"
                        )
                    change_provider_status(
                        scraper, f"{'en' if success else 'dis'}abled"
                    )
            else:
                change_provider_status(scraper, "enabled")
        else:
            change_provider_status(scraper, "disabled")

    common.set_setting("general.firstrun", "false")
