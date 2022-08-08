# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

from datetime import datetime
from platform import machine, system
import uuid
from xml.etree import ElementTree

import requests

import xbmc
import xbmcgui

import requests
from requests.exceptions import RequestException

from providerModules.a4kOfficial import common

from resources.lib.common import tools
from resources.lib.modules.globals import g


class Plex:
    def __init__(self, client_id=None, token=None):
        self._base_url = "https://plex.tv"
        self._auth_url = self._base_url + "/link/"
        self._token = token or common.get_setting("plex.token")
        self._client_id = client_id or common.get_setting("plex.client_id")
        self._device_id = common.get_setting("plex.device_id")

        self.dialog = None
        self.progress = None

        self._headers = {
            "X-Plex-Device-Name": "a4kOfficial",
            "X-Plex-Product": "Seren",
            "X-Plex-Version": "1.3.0",
            "X-Plex-Platform": "Kodi",
            "X-Plex-Platform-Version": common.get_kodi_version(),
            "X-Plex-Device": system(),
            "X-Plex-Model": machine(),
            "X-Plex-Provides": "player",
            "X-Plex-Client-Identifier": self._client_id or str(hex(uuid.getnode())),
            "Accept": "application/json",
        }
        if self._token:
            self._headers["X-Plex-Token"] = self._token

    def _get(self, url, **kwargs):
        try:
            return requests.get(url, **kwargs)
        except RequestException as re:
            try:
                return requests.get(url, verify=True, **kwargs)
            except RequestException as re:
                common.log(f"a4kOfficial: Could not access Plex. {re}", "error")

    def auth(self):
        self.progress = xbmcgui.DialogProgress()
        self._start_auth_time = datetime.utcnow().timestamp()

        self._token = None
        url = self._base_url + "/pins"
        data = requests.post(url, headers=self._headers)

        if data.status_code != 201:
            common.log(
                "Failed to authorize Plex: {} response from {}".format(
                    data.status_code, url
                )
            )

        try:
            pin = data.json().get("pin", {})
            code = pin.get("code", "")
            self._device_id = pin.get("id", "")
            self._expire_auth_time = datetime.strptime(
                pin.get("expires-at", ""), "%Y-%m-%dT%H:%M:%SZ"
            ).timestamp()
        except Exception as e:
            common.log("a4kOfficial: Failed to authorize Plex: {}".format(e), "error")
            return

        tools.copy2clip(code)
        self._check_url = self._base_url + "/pins/{}".format(self._device_id)

        self.progress.create("a4kOfficial: Plex Authorization")

        while self._token is None:
            current_auth_time = datetime.utcnow().timestamp()
            if self.progress.iscanceled() or current_auth_time > self._expire_auth_time:
                self.progress.close()
                break
            self.auth_loop(code, current_auth_time)

        return self._token is not None

    def auth_loop(self, code, current_auth_time):
        self.progress.update(
            int(
                (
                    float(current_auth_time - self._start_auth_time)
                    / float(self._expire_auth_time - self._start_auth_time)
                )
                * 100
            ),
            g.get_language_string(30018).format(g.color_string(self._auth_url))
            + "\n"
            + g.get_language_string(30019).format(g.color_string(code))
            + "\n"
            + g.get_language_string(30047),
        )

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
            pin = data.json().get("pin", {})
            self._token = pin.get("auth_token", "")
            self._client_id = pin.get("client_identifier", "")
        except Exception:
            self._token = None
            self._client_id = None

        if self._token:
            self.progress.close()
            self._headers.update(
                {
                    "X-Plex-Client-Identifier": self._client_id,
                    "X-Plex-Token": self._token,
                }
            )

            common.set_setting("plex.token", self._token)
            common.set_setting("plex.client_id", self._client_id)

            device_id = self.get_device_id()
            if device_id is not None:
                common.set_setting("plex.device_id", device_id)

            self.dialog.ok("a4kOfficial", "Successfully authenticated with Plex.")

    def get_device_id(self):
        url = self._base_url + "/devices.xml"
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
                device_token = device.get("token", "")
                if device_token == self._token:
                    return device.get("id")
        except Exception as e:
            common.log("a4kOfficial: Failed to authorize Plex: {}".format(e), "error")
            return

    def get_resources(self):
        url = self._base_url + "/api/v2/resources"
        results = self._get(url, params={"includeHttps": 1}, headers=self._headers)

        if results is not None and results.status_code != 200:
            common.log(
                f"Failed to list Plex resources: {results.status_code} response from {url}"
            )
            return

        listings = []
        try:
            data = results.json()
            for resource in data:
                if "server" in resource.get("provides", ""):
                    access_token = resource.get("accessToken", "")
                    if not access_token:
                        continue

                    connections = resource.get("connections", [])
                    for connection in connections:
                        url = connection.get("uri", "")
                        local = int(connection.get("local", True))

                        if ".plex.direct" in url and not local:
                            listings.append((url, access_token))
        except Exception as e:
            common.log(f"a4kOfficial: Failed to list Plex resources: {e}")
            return

        return listings

    def search(self, resource, query, **kwargs):
        kwargs.pop("type", "movie")
        url = resource[0] + "/search"
        params = {"query": query}
        params.update(**kwargs)
        self._headers["X-Plex-Token"] = resource[1]

        results = self._get(url, params=params, headers=self._headers)
        self._headers["X-Plex-Token"] = self._token
        if results and results.ok:
            return results.json().get("MediaContainer", {}).get("Metadata", [])
