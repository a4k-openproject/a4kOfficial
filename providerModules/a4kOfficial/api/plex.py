# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

import uuid
from xml.etree import ElementTree

import requests

import xbmc
import xbmcgui

from providerModules.a4kOfficial import common

from resources.lib.modules.globals import g
from resources.lib.common import tools


class Plex:
    def __init__(self):
        self._base_url = "https://plex.tv"
        self._auth_url = self._base_url + "/link/"
        self._token = common.get_setting("plex.token")
        self._client_id = common.get_setting("plex.client_id")
        self._device_id = common.get_setting("plex.device_id")

        self.dialog = None
        self.progress = None

        self._headers = {
            "X-Plex-Device-Name": "a4kOfficial",
            "X-Plex-Product": "Seren",
            "X-Plex-Version": "1.1.1",
            "X-Plex-Platform": "Kodi",
            "X-Plex-Platform-Version": common.get_kodi_version(),
            "X-Plex-Device": common.get_platform_system(),
            "X-Plex-Model": common.get_platform_machine(),
            "X-Plex-Provides": "player",
            "X-Plex-Client-Identifier": str(hex(uuid.getnode())),
        }

    def auth(self):
        self.progress = xbmcgui.DialogProgress()

        self._token = None
        url = self._base_url + "/pins.xml"
        data = requests.post(url, headers=self._headers)

        if data.status_code != 201:
            common.log(
                "Failed to authorize Plex: {} response from {}".format(
                    data.status_code, url
                )
            )

        try:
            pin = ElementTree.fromstring(data.text)
            code = pin.find("code").text
            self._device_id = pin.find("id").text
        except Exception as e:
            common.log("a4kOfficial: Failed to authorize Plex: {}".format(e), "error")
            return

        tools.copy2clip(code)
        self.progress.create("a4kOfficial: Plex Authorization")
        self.progress.update(
            0,
            g.get_language_string(30018).format(g.color_string(self._auth_url))
            + '\n'
            + g.get_language_string(30019).format(g.color_string(code))
            + '\n'
            + g.get_language_string(30047),
        )
        self._check_url = self._base_url + "/pins/{}.xml".format(self._device_id)
        xbmc.sleep(2000)

        while self._token is None:
            if self.progress.iscanceled():
                self.progress.close()
                break
            self.auth_loop()

        return self._token is not None

    def auth_loop(self):
        xbmc.sleep(5000)
        data = requests.get(self._check_url, headers=self._headers)

        if data.status_code != 200:
            common.log(
                "Failed to authorize Plex: {} response from {}".format(
                    data.status_code, self._check_url
                )
            )
            return

        try:
            pin = ElementTree.fromstring(data.text)
            self._token = pin.find("auth_token").text
            self._client_id = pin.find("client-identifier").text
        except Exception:
            self._token = None
            self._client_id = None

        if self._token:
            self.progress.close()
            common.set_setting("plex.token", self._token)
            common.set_setting("plex.client_id", self._client_id)
            xbmc.sleep(500)

            device_id = self.get_device_id()
            if device_id is not None:
                common.set_setting("plex.device_id", device_id)

    def get_device_id(self):
        url = (
            self._base_url
            + "/devices.xml?X-Plex-Client-Identifier={}&X-Plex-Token={}".format(
                self._client_id, self._token
            )
        )
        results = requests.get(url, headers=self._headers)

        if results.status_code != 200:
            common.log(
                "Failed to authorize Plex: {} response from {}".format(
                    results.status_code, url
                )
            )
            return

        try:
            container = ElementTree.fromstring(results.text)
            devices = container.findall("Device")
            for device in devices:
                device_token = device.get("token")
                if device_token == self._token:
                    return device.get("id")
        except Exception as e:
            common.log("a4kOfficial: Failed to authorize Plex: {}".format(e), "error")
            return

    def revoke(self):
        url = "https://www.plex.tv/devices/{}.xml?X-Plex-Token={}".format(
            self._device_id, self._token
        )
        result = requests.delete(url)

        if result.status_code != 200:
            common.log(
                "Failed to revoke Plex authorization: {} response from {}".format(
                    result.status_code, url
                )
            )

        for setting in ["plex.token", "plex.client_id", "plex.device_id"]:
            common.set_setting(setting, "")
