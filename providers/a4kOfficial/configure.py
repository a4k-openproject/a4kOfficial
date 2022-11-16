# -*- coding: utf-8 -*-
import importlib
import requests

import xbmcgui

from resources.lib.modules.globals import g

from providerModules.a4kOfficial import common, ADDON_IDS


_ipify = "https://api.ipify.org?format=json"
_ipinfo = "https://ipinfo.io/{}/json"


def setup(*args, **kwargs):
    common.set_setting("justwatch.country", _get_country_code() or "US")

    dialog = xbmcgui.Dialog()
    providers = {p['provider_name']: p for p in common.get_package_providers()}
    automatic = [_get_provider_status(scraper, kwargs.get("first_run"), providers) for scraper in ADDON_IDS]

    choices = (
        dialog.multiselect(
            "a4kOfficial: Choose providers to enable",
            [ADDON_IDS[i[0]]["name"] for i in automatic],
            preselect=[i for i in range(len(automatic)) if automatic[i][1]],
        )
        or []
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
                        common.log(f"a4kOfficial.{scraper}: Setup not complete; disabling")
                    common.change_provider_status(scraper, f"{'en' if success else 'dis'}abled")
            else:
                common.change_provider_status(scraper, "enabled")
        else:
            common.change_provider_status(scraper, "disabled")

    return False


def _get_current_ip():
    data = requests.get(_ipify)
    if data.ok:
        return data.json().get("ip", "0.0.0.0")


def _get_country_code():
    ip = _get_current_ip()
    data = requests.get(_ipinfo.format(ip))

    if data.ok:
        return data.json().get("country", "US")


def _get_provider_status(scraper=None, initial=False, providers=[]):
    if initial:
        status = common.check_for_addon(ADDON_IDS[scraper]["plugin"])
    else:
        status = True if providers[scraper]["status"] == "enabled" else False
    return (scraper, status)


if common.get_setting("general.firstrun"):
    first_run = setup(first_run=True)
    common.set_setting("general.firstrun", first_run)
