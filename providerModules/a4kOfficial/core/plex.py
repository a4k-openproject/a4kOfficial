# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

import pickle
import os
from urllib.parse import quote

import xbmcaddon
import xbmcvfs

from providerModules.a4kOfficial import ADDON_IDS, common
from providerModules.a4kOfficial.api.plex import Plex
from providerModules.a4kOfficial.core import Core

from resources.lib.common.source_utils import (
    check_title_match,
    clean_title,
    get_info,
    get_quality,
    de_string_size,
)
from resources.lib.modules.exceptions import PreemptiveCancellation

PLEX_AUDIO = {"dca": "dts", "dca-ma": "hdma"}


class PlexCore(Core):
    def __init__(self):
        super(PlexCore, self).__init__()
        self._plugin = ADDON_IDS[self._scraper]["plugin"]
        client_id, token = self._get_auth()
        self._api = Plex(client_id, token)
        self._resources = self._api.get_resources()

    def _get_auth(self):
        addon = xbmcaddon.Addon(self._plugin)
        client_id = addon.getSetting("client_id")

        addon_path = xbmcvfs.translatePath(addon.getAddonInfo("profile"))
        cache_path = os.path.join(
            addon_path, "cache", "servers", "plexhome_user.pcache"
        )
        with open(cache_path, "rb") as f:
            cache = pickle.load(f)

        token = cache.get("myplex_user_cache").split("|")[1]

        return client_id, token

    def __make_query(self, resource, query, **kwargs):
        result = self._api.search(resource, query, **kwargs)

        return result

    def _make_show_query(self, resource, episode_title):
        result = self.__make_query(resource, episode_title, type="episode")

        return result

    def _make_movie_query(self, resource, title, year):
        result = self.__make_query(resource, title, year=year, type="movie")

        return result

    def _process_show_item(self, resource, item, simple_info, all_info):
        source = None

        try:
            type = item.get("type", "")
            media = item.get("Media", [{}])[0]
            key = item.get("key", "")
            show_title = item.get("grandparentTitle", "")
            episode_title = item.get("title", "")
            season = item.get("parentIndex", 0)
            episode = item.get("index", 0)
            source_title = item.get("sourceTitle", "")

            quality = media.get("videoResolution", "Unknown")
            part = media.get("Part", [{}])[0]
            info = " ".join(
                [
                    media.get("container", ""),
                    media.get("videoCodec", ""),
                    media.get("videoProfile", ""),
                    PLEX_AUDIO.get(
                        media.get("audioCodec"), media.get("audioCodec", "")
                    ),
                    media.get("audioProfile", ""),
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
        if "/" in file:
            filename = file.rsplit("/", 1)[-1]
        elif "\\" in file:
            filename = file.rsplit("\\", 1)[-1]

        if type != "episode":
            return
        elif not (
            season == simple_info["season_number"]
            and episode == simple_info["episode_number"]
        ):
            return
        elif not (
            clean_title(simple_info["show_title"]) == clean_title(show_title)
            and clean_title(simple_info["episode_title"]) == clean_title(episode_title)
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

    def _process_movie_item(self, resource, item, simple_info, all_info):
        source = None

        try:
            type = item.get("type", "")
            media = item.get("Media", [{}])[0]
            key = item.get("key", "")
            title = item.get("title", "")
            source_title = item.get("sourceTitle", "")

            year = int(media.get("year", simple_info["year"]))
            quality = media.get("videoResolution", "Unknown")
            part = media.get("Part", [{}])[0]
            info = " ".join(
                [
                    media.get("container", ""),
                    media.get("videoCodec", ""),
                    media.get("videoProfile", ""),
                    PLEX_AUDIO.get(
                        media.get("audioCodec"), media.get("audioCodec", "")
                    ),
                    media.get("audioProfile", ""),
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
        if "/" in file:
            filename = file.rsplit("/", 1)[-1]
        elif "\\" in file:
            filename = file.rsplit("\\", 1)[-1]

        if type != "movie":
            return
        elif year < int(simple_info["year"]) - 1 or year > int(simple_info["year"]) + 1:
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

    def episode(self, simple_info, all_info):
        for resource in self._resources:
            try:
                items = self._make_show_query(resource, simple_info["episode_title"])

                for item in items:
                    source = self._process_show_item(
                        resource, item, simple_info, all_info
                    )
                    if source is not None:
                        self.sources.append(source)
                        break
            except PreemptiveCancellation:
                return self._return_results("episode", self.sources, preemptive=True)

        return self._return_results("episode", self.sources)

    def movie(self, simple_info, all_info):
        for resource in self._resources:
            queries = []
            queries.append(simple_info["title"])
            queries.extend(simple_info.get("aliases", []))

            try:
                items = []
                for query in queries:
                    items.extend(
                        self._make_movie_query(
                            resource, query, int(simple_info["year"])
                        )
                    )

                for item in items:
                    source = self._process_movie_item(
                        resource, item, simple_info, all_info
                    )
                    if source is not None:
                        self.sources.append(source)
                        break
            except PreemptiveCancellation:
                return self._return_results("movie", self.sources, preemptive=True)

        return self._return_results("movie", self.sources)

    @staticmethod
    def get_listitem(return_data):
        scraper = return_data["scraper"]
        if not common.check_for_addon(ADDON_IDS[scraper]["plugin"]):
            common.log(
                "a4kOfficial: '{}' is not installed; disabling '{}'".format(
                    ADDON_IDS[scraper]["plugin"],
                    scraper,
                ),
                "info",
            )
            common.change_provider_status(scraper, "disabled")
        else:
            return super(PlexCore, PlexCore).get_listitem(return_data)
