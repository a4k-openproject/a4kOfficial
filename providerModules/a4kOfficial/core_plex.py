# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

from datetime import datetime
from urllib.parse import quote
import uuid
from xml.etree import ElementTree

import requests

import xbmc
import xbmcgui

from providerModules.a4kOfficial import common
from providerModules.a4kOfficial.common import ADDON_IDS
from providerModules.a4kOfficial.core import Core

from resources.lib.common.source_utils import (
    check_episode_number_match,
    check_title_match,
    clean_title,
    get_info,
    get_quality,
    de_string_size,
)
from resources.lib.common import tools
from resources.lib.modules.exceptions import PreemptiveCancellation
from resources.lib.modules.globals import g

PLEX_AUDIO = {'dca': 'dts', 'dca-ma': 'hdma'}


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
            "X-Plex-Client-Identifier": self._client_id or str(hex(uuid.getnode())),
            "Accept": "application/json",
        }
        if self._token:
            self._headers["X-Plex-Token"] = self._token

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
            + '\n'
            + g.get_language_string(30019).format(g.color_string(code))
            + '\n'
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
        results = requests.get(url, params={"includeHttps": 1}, headers=self._headers)

        if results.status_code != 200:
            common.log(
                "Failed to list Plex resources: {} response from {}".format(
                    results.status_code, url
                )
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
            common.log(
                "a4kOfficial: Failed to list Plex resources: {}".format(e), "error"
            )
            return

        return listings

    def search(self, resource, query, **kwargs):
        media_type = kwargs.pop("type", "movie")
        url = resource[0] + "/{}search".format(
            "hubs/" if media_type == "episode" else ""
        )
        params = {"query": query}
        params.update(**kwargs)
        self._headers["X-Plex-Token"] = resource[1]

        results = requests.get(url, params=params, headers=self._headers)
        self._headers["X-Plex-Token"] = self._token
        if results.ok:
            return results.json().get("MediaContainer", {}).get("Metadata", [])

    def revoke(self):
        url = "https://www.plex.tv/devices/{}.xml".format(self._device_id)
        result = requests.delete(url)

        if result.status_code != 200:
            common.log(
                "Failed to revoke Plex authorization: {} response from {}".format(
                    result.status_code, url
                )
            )

        for setting in ["plex.token", "plex.client_id", "plex.device_id"]:
            common.set_setting(setting, "")


class PlexCore(Core):
    def __init__(self):
        super(PlexCore, self).__init__()
        self._api = Plex()
        self._plugin = ADDON_IDS[self._scraper]["plugin"]
        self._resources = self._api.get_resources()

    def __make_query(self, resource, query, **kwargs):
        result = self._api.search(resource, query, **kwargs)

        return result

    def _make_show_query(self, resource, show_title):
        result = {}

        return result.get("tvshows", {})

    def _make_movie_query(self, resource, title, year):
        result = self.__make_query(resource, title, year=year, type="movie")

        return result

    def _process_show_item(self, resource, item, all_info):
        source = None

        # source = {
        #     "scraper": self._scraper,
        #     "release_title": db_details['label'],
        #     "info": source_info['info'],
        #     "size": source_info['size'],
        #     "quality": source_info['quality'],
        #     "url": db_details.get('file', ''),
        # }

        return source

    def _process_movie_item(self, resource, item, simple_info):
        source = None

        try:
            type = item.get("type", "")
            media = item.get("Media", [{}])[0]
            key = item.get("key", "")
            source_title = item.get("sourceTitle", "")

            year = int(media.get("year", simple_info["year"]))
            quality = media.get("videoResolution", "Unknown")
            part = media.get("Part", [{}])[0]
            info = ' '.join(
                [
                    media.get("container", ''),
                    media.get("videoCodec", ''),
                    media.get("videoProfile", ''),
                    PLEX_AUDIO.get(
                        media.get("audioCodec"), media.get("audioCodec", '')
                    ),
                    media.get("audioProfile", ''),
                    str(media.get("audioChannels", "2")) + "ch",
                ]
            )

            size = str(int(part.get("size", 0)) / 1024 / 1024) + "MiB"
            file = part.get("file", "")
        except Exception as e:
            common.log(
                "a4kOfficial: Failed to process Plex source: {}".format(e), "error"
            )
            return

        filename = file
        if '/' in file:
            filename = file.rsplit('/', 1)[-1]
        elif '\\' in file:
            filename = file.rsplit('\\', 1)[-1]

        if type != "movie":
            return
        elif year < int(simple_info["year"]) - 1 or year > int(simple_info["year"]) + 1:
            return
        elif not check_title_match(
            clean_title(simple_info["title"]).split(" "),
            clean_title(filename),
            simple_info,
        ):
            return

        url = quote(resource[0] + key)

        source = {
            "scraper": self._scraper,
            "release_title": filename,
            "info": get_info(filename).union(get_info(info)),
            "size": de_string_size(size),
            "quality": get_quality(quality),
            "url": self._movie_url.format(self._plugin, url),
            "debrid_provider": source_title,
        }

        return source

    # def episode(self, simple_info, all_info):
    #     for url in self._resources:
    #         try:
    #             items = self._make_show_query(url, simple_info["show_title"])

    #             for item in items:
    #                 source = self._process_show_item(url, item, all_info)
    #                 if source is not None:
    #                     self.sources.append(source)
    #                     break
    #         except PreemptiveCancellation:
    #             return self._return_results("episode", self.sources, preemptive=True)

    #     return self._return_results("episode", self.sources)

    def movie(self, simple_info, all_info):
        for resource in self._resources:
            queries = []
            queries.append(simple_info['title'])
            queries.extend(simple_info.get('aliases', []))

            try:
                items = []
                for query in queries:
                    items.extend(
                        self._make_movie_query(
                            resource, query, int(simple_info['year'])
                        )
                    )

                for item in items:
                    source = self._process_movie_item(resource, item, simple_info)
                    if source is not None:
                        self.sources.append(source)
                        break
            except PreemptiveCancellation:
                return self._return_results("movie", self.sources, preemptive=True)

        return self._return_results("movie", self.sources)

    @staticmethod
    def get_listitem(return_data):
        scraper = return_data['scraper']
        if not common.check_for_addon(ADDON_IDS[scraper]["plugin"]):
            common.log(
                "a4kOfficial: '{}' is not installed; disabling '{}'".format(
                    ADDON_IDS[scraper]["plugin"],
                    scraper,
                ),
                'info',
            )
            common.change_provider_status(scraper, "disabled")
        else:
            return super(Core, Core).get_listitem(return_data)
