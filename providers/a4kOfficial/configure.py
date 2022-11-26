# -*- coding: utf-8 -*-
import importlib
import os
import requests
import sqlite3
import time
import zipfile

import xbmcgui
import xbmcvfs

from resources.lib.modules.globals import g

from providerModules.a4kOfficial import common, ADDON_IDS, REPO_ADDRESS, REPO_ID


_ipify = "https://api.ipify.org?format=json"
_ipinfo = "https://ipinfo.io/{}/json"

_home = xbmcvfs.translatePath("special://home")
_addons = os.path.join(_home, "addons")
_database = xbmcvfs.translatePath("special://database")
_packages = os.path.join(_addons, "packages")
_temp = xbmcvfs.translatePath("special://temp")


def _exists(addon):
    params = {"method": "Addons.GetAddons"}

    addons = common.execute_jsonrpc(**params)
    exists = False
    if addon in [a.get("addonid") for a in addons.get("result", {}).get("addons", {})]:
        exists = True

    common.log("{} {} installed".format(addon, "is" if exists else "not"))
    return exists


def _get_addons_db():
    for db in os.listdir(_database):
        if db.lower().startswith("addons") and db.lower().endswith(".db"):
            return os.path.join(_database, db)


def _set_enabled(addon, enabled, exists=True):
    enabled_params = {
        "method": "Addons.GetAddonDetails",
        "params": {"addonid": addon, "properties": ["enabled"]},
    }

    params = {
        "method": "Addons.SetAddonEnabled",
        "params": {"addonid": addon, "enabled": enabled},
    }

    if not exists and not enabled:
        return False
    elif not exists and enabled:
        db_file = _get_addons_db()
        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()
        date = time.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("DELETE FROM installed WHERE addonID = ?", (addon,))
        cursor.execute(
            "INSERT INTO installed (addonID, enabled, installDate) VALUES (?, 1, ?)",
            (addon, date),
        )
        connection.commit()

        connection.close()
    else:
        common.execute_jsonrpc(**params)

    new_status = (
        common.execute_jsonrpc(**enabled_params).get("result", {}).get("addon", {}).get("enabled", enabled)
    ) == enabled

    common.log("{}{}{}abled".format(addon, " " if new_status else " not ", "en" if enabled else "dis"))
    return new_status


def _install_repo_zip(url):
    if download_path := _download_repo_zip(url):
        _extract_repo_zip(download_path)
        _set_enabled(REPO_ID, True, _exists(REPO_ID))
        common.execute_builtin("UpdateLocalAddons()")
        common.execute_builtin("UpdateLocalRepos()")


def _download_repo_zip(url):
    if (repo_zip := requests.get(url)).ok:
        path = os.path.join(_packages, url.split('/')[-1])
        try:
            with xbmcvfs.File(path, "w") as zip_file:
                zip_file.write(repo_zip.content)
        except Exception as e:
            common.log(f"Couldn't download repository zip: {e}")
            return None
        else:
            return path


def _extract_repo_zip(zip_location):
    with zipfile.ZipFile(zip_location) as file:
        base_directory = file.namelist()[0].split('/')[0]
        for f in file.namelist():
            try:
                file.extract(f, _temp)
            except Exception as e:
                common.log("Could not extract {}: {}".format(f, e))

    install_path = os.path.join(_addons, REPO_ID)
    common.copytree(os.path.join(_temp, base_directory), install_path, ignore=True)
    common.remove_folder(os.path.join(_temp, base_directory))
    common.remove_file(zip_location)


def setup(*args, **kwargs):
    common.set_setting("justwatch.country", _get_country_code() or "US")

    dialog = xbmcgui.Dialog()

    if dialog.yesno(
        "a4kOfficial: Repo Installation",
        "Do you want to install a4kOfficial Repository, for easier installation of supported add-ons?",
    ):
        _install_repo_zip(REPO_ADDRESS)

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
