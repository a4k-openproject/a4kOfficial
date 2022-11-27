# -*- coding: utf-8 -*-
import math
import os
import requests
from requests.exceptions import RequestException
import shutil
import sys

import xbmc
import xbmcvfs

from resources.lib.common import provider_tools
from resources.lib.modules.globals import g
from resources.lib.modules.providers.install_manager import ProviderInstallManager

from providerModules.a4kOfficial import PACKAGE_NAME


def log(msg, level="info"):
    g.log(f"{msg}", level)


def get_setting(id):
    return provider_tools.get_setting(PACKAGE_NAME, id)


def set_setting(id, value):
    return provider_tools.set_setting(PACKAGE_NAME, id, value)


def change_provider_status(scraper=None, status="enabled"):
    ProviderInstallManager().flip_provider_status("a4kOfficial", scraper, status)


def check_for_addon(plugin):
    if plugin is None:
        return None

    status = execute_jsonrpc("Addon.GetAddonDetails", {"addonid": plugin, "properties": ["enabled", "installed"]})
    if status.get("error"):
        return False
    else:
        addon = status.get("result", {}).get("addon", {})
        installed = addon.get("installed")
        enabled = addon.get("enabled")
        if installed and enabled:
            return True
        elif installed and not enabled:
            return "disabled"
        else:
            return False


def check_url(url):
    try:
        return requests.get(url).ok
    except RequestException as re:
        log(f"a4kOfficial: Could not access {url}. {re}", "error")
        return False


def get_all_relative_py_files(file):
    files = os.listdir(os.path.dirname(file))
    return [filename[:-3] for filename in files if not filename.startswith("__") and filename.endswith(".py")]


def parseDOM(html, name="", attrs=None, ret=False):
    if attrs:
        import re

        attrs = dict((key, re.compile(value + ("$" if value else ""))) for key, value in attrs.items())
    from providerModules.a4kOfficial import dom_parser

    results = dom_parser.parse_dom(html, name, attrs, ret)

    if ret:
        results = [result.attrs[ret.lower()] for result in results]
    else:
        results = [result.content for result in results]

    return results


def execute_jsonrpc(method, params=None):
    import json

    call_params = {"id": 1, "jsonrpc": "2.0", "method": method}
    if params:
        call_params.update({"params": params})
    call = json.dumps(call_params)
    response = xbmc.executeJSONRPC(call)
    return json.loads(response)


def execute_builtin(method):
    xbmc.executebuiltin(method)


def convert_size(size_bytes):
    size_bytes = int(size_bytes)
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s}{size_name[i]}"


def get_kodi_version(short=False):
    version = xbmc.getInfoLabel("System.BuildVersion")
    if short:
        version = int(version[:2])
    return version


def get_system_platform():
    platform = "unknown"
    for p in ["android", "linux", "uwp", "windows", "osx", "ios", "tvos"]:
        if xbmc.getCondVisibility(f"system.platform.{p}"):
            platform = p

    return platform


def get_package_providers():
    manager = ProviderInstallManager()
    providers = manager.known_providers

    return [p for p in providers if p["package"] == PACKAGE_NAME]


def get_infoboolean(label):
    return xbmc.getCondVisibility(label)


def remove_folder(path):
    if xbmcvfs.exists(ensure_path_is_dir(path)):
        log("Removing {}".format(path))
        try:
            shutil.rmtree(path)
        except Exception as e:
            log("Error removing {}: {}".format(path, e))


def remove_file(path):
    if xbmcvfs.exists(path):
        log("Removing {}".format(path))
        try:
            os.remove(path)
        except Exception as e:
            log("Error removing {}: {}".format(path, e))


def read_from_file(file_path, bytes=False):
    content = None
    try:
        f = xbmcvfs.File(file_path, "r")
        if bytes:
            content = f.readBytes()
        else:
            content = f.read()
    except IOError:
        return None
    finally:
        try:
            f.close()
        except:
            pass
    return content


def write_to_file(file_path, content):
    try:
        f = xbmcvfs.File(file_path, "w")
        return f.write(content)
    except IOError:
        return None
    finally:
        try:
            f.close()
        except:
            pass


def ensure_path_is_dir(path):
    if not path.endswith("\\") and sys.platform == "win32":
        if path.endswith("/"):
            path = path.split("/")[0]
        return path + "\\"
    elif not path.endswith("/"):
        return path + "/"
    return path


def create_folder(path):
    path = ensure_path_is_dir(path)
    if not xbmcvfs.exists(path):
        xbmcvfs.mkdir(path)


def copytree(src, dst, symlinks=False, ignore=None):
    create_folder(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            remove_file(d)
            shutil.copy2(s, d)
