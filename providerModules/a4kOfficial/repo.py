from base64 import b64decode
import os
import sqlite3
import time

import xbmc
import xbmcvfs

from providerModules.a4kOfficial import common


_home = xbmcvfs.translatePath("special://home")
_addons = os.path.join(_home, "addons")
_database = xbmcvfs.translatePath("special://database")

REPO_ID = "repository.a4kOfficial"
REPO_XML = "repo_addon.xml"
REPO_ICON = "repo_icon.b64"


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


def install_repo():
    repo_path = os.path.join(_addons, REPO_ID)
    xml_path = os.path.join(repo_path, REPO_XML)
    icon_path = os.path.join(repo_path, "icon.png")
    repo_xml_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), REPO_XML)
    icon_content_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), REPO_ICON)
    repo_xml_content = common.read_from_file(repo_xml_path)
    icon_content = common.read_from_file(icon_content_path, bytes=True)

    common.create_folder(repo_path)
    common.write_to_file(xml_path, repo_xml_content)
    common.write_to_file(icon_path, icon_content)

    _set_enabled(REPO_ID, True, _exists(REPO_ID))
    common.execute_builtin("UpdateLocalAddons()")
    common.execute_builtin("UpdateLocalRepos()")
    while not common.check_for_addon(REPO_ID):
        xbmc.sleep(500)
