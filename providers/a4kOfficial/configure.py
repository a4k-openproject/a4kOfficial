# -*- coding: utf-8 -*-
import importlib
import requests
import time

import xbmc
import xbmcgui

from resources.lib.modules.globals import g

from providerModules.a4kOfficial import common, ADDON_IDS
from providerModules.a4kOfficial.repo import install_repo, REPO_ID

_ipify = "https://api.ipify.org?format=json"
_ipinfo = "https://ipinfo.io/{}/json"


def setup(*args, **kwargs):
    common.set_setting("justwatch.country", _get_country_code() or "US")

    dialog = xbmcgui.Dialog()

    if not common.check_for_addon(REPO_ID):
        if dialog.yesno(
            "a4kOfficial: Repo Installation",
            "Do you want to install a4kOfficial Repository, for easier installation of supported add-ons?"
            " This repository serves all of the third-party add-ons that are supported by this package, from their official sources."
            " Services which are enabled in the following prompt will be offered for installation, but only if this repository is installed.",
        ):
            install_repo()

    providers = {p['provider_name']: p for p in common.get_package_providers()}
    automatic = [_get_provider_status(scraper, kwargs.get("first_run"), providers) for scraper in ADDON_IDS]

    choices = (
        dialog.multiselect(
            "a4kOfficial: Service Selection",
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

            if (
                (plugin := ADDON_IDS[scraper]['plugin']) is not None
                and not common.check_for_addon(plugin)
                and common.check_for_addon(REPO_ID)
            ):
                common.execute_builtin(f"InstallAddon({plugin})")
                start = time.time()
                timeout = 10
                while not common.check_for_addon(plugin):
                    if time.time() >= start + timeout:
                        break

                    time.sleep(0.5)

            if hasattr(provider, "setup"):
                if dialog.yesno(
                    "a4kOfficial: Provider Setup",
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

    common.set_setting("general.firstrun", 0)


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
    setup(first_run=True)
