# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

import re
import uuid

import requests

import xbmc
import xbmcgui

from providerModules.a4kOfficial import common


class Plex:
    def __init__(self):
        self._base_url = "https://www.plex.tv"
        self._auth_url = self._base_url + "/link/"
        self._token = common.get_setting("plex.token")
        self._client_id = common.get_setting("plex.client_id")
        self._device_id = common.get_setting("plex.device_id")

        self.dialog = None
        self.progress = None

        self._headers = {
            "X-Plex-Device-Name": "a4kOfficial",
            "X-Plex-Product": "PlexNet",
            "X-Plex-Version": "0.3.4",
            "X-Plex-Platform": "Kodi",
            "X-Plex-Platform-Version": common.get_kodi_version(),
            "X-Plex-Device": common.get_platform_system(),
            "X-Plex-Model": common.get_platform_machine(),
            "X-Plex-Provides": "player",
            "X-Plex-Client-Identifier": str(hex(uuid.getnode())),
        }

    def auth(self):
        self.progress = xbmcgui.DialogProgress()

        self._token = ''
        url = self._base_url + "/pins.xml"
        data = requests.post(url, headers=self._headers)

        if data.status_code != 201:
            raise Exception

        code = re.search(r"<code>(.*?)</code>", data.text, re.I).group(1)
        self._device_id = re.search(r"<id.+?>(.*?)</id>", data.text, re.I).group(1)
        self.progress.create("a4kOfficial: Plex Authorization")
        self.progress.update(
            0,
            "To authorize, visit the following page:\n{}\nAnd enter the code: {}".format(
                self._auth_url, code
            ),
        )
        self._check_url = self._base_url + "/pins/{}.xml".format(self._device_id)
        xbmc.sleep(2000)

        while not self._token:
            if self.progress.iscanceled():
                self.progress.close()
                break
            self.auth_loop()

    def auth_loop(self):
        xbmc.sleep(5000)
        data = requests.get(self._check_url, headers=self._headers)

        if data.status_code != 200:
            raise Exception

        try:
            self._token = re.search(
                r"<auth_token>(.*?)</auth_token>", data.text, re.I
            ).group(1)
        except Exception:
            self.token = ''

        if self._token:
            self._client_id = re.search(
                r"<client-identifier>(.*?)</client-identifier>", data.text, re.I
            ).group(1)
            self.progress.close()
            common.set_setting("plex.token", self._token)
            common.set_setting("plex.client_id", self._client_id)
            xbmc.sleep(500)

            new_id = self.get_auth_id()
            common.set_setting("plex.device_id", new_id)

    def get_auth_id(self):
        url = (
            self._base_url
            + "/devices.xml?&X-Plex-Client-Identifier={}&X-Plex-Token={}".format(
                self._client_id, self._token
            )
        )
        results = requests.get(url, headers=self._headers)

        if results.status_code != 200:
            raise Exception

        devices = re.findall(
            r"(<Device\s.+?</Device>)", results.text, flags=re.M | re.S
        )
        for device in devices:
            device_token = common.parseDOM(device, "Device", ret="token")[0]
            if device_token != self._token:
                continue

            return common.parseDOM(device, "Device", ret="id")[0]
