# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

from platform import machine, system
import uuid

import requests

from providerModules.a4kOfficial import common


class Plex:
    def __init__(self, client_id=None, token=None):
        self._base_url = "https://plex.tv"
        self._auth_url = self._base_url + "/link/"
        self._token = token
        self._client_id = client_id

        self.dialog = None
        self.progress = None

        self._headers = {
            "X-Plex-Device-Name": "a4kOfficial",
            "X-Plex-Product": "Seren",
            "X-Plex-Version": "1.1.1",
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

    def get_resources(self):
        url = self._base_url + "/api/v2/resources"
        results = requests.get(url, params={"includeHttps": 1}, headers=self._headers)

        if results.status_code != 200:
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

        results = requests.get(url, params=params, headers=self._headers)
        self._headers["X-Plex-Token"] = self._token
        if results.ok:
            return results.json().get("MediaContainer", {}).get("Metadata", [])
