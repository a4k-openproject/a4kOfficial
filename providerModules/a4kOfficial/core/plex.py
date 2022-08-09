# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

import pickle
import os

import xbmcaddon
import xbmcvfs

from providers.a4kOfficial import configure
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
        self._client_id, self._token = self._get_auth()
        self._api = Plex(self._client_id, self._token)
        self._resources = self._api.get_resources()

        self._base_url = None
        self._movie_url = None
        self._episode_url = None

    def _get_auth(self):
        if self._plugin:
            addon = xbmcaddon.Addon(self._plugin)
            client_id = addon.getSetting("client_id")

            addon_path = xbmcvfs.translatePath(addon.getAddonInfo("profile"))
            cache_path = os.path.join(
                addon_path, "cache", "servers", "plexhome_user.pcache"
            )
            with open(cache_path, "rb") as f:
                cache = pickle.load(f)

            token = cache.get("myplex_user_cache").split("|")[1]
        else:
            client_id = common.get_setting("plex.client_id")
            token = common.get_setting("plex.token")

        return client_id, token

    def _make_source(self, item, url, **kwargs):
        source = super(PlexCore, self)._make_source(item, url, **kwargs)

        source.update(
            {
                "release_title": item["filename"],
                "info": get_info(item["filename"]).union(get_info(item["info"])),
                "size": de_string_size(item["size"]),
                "quality": get_quality(f"{item['filename']} ({item['quality']})"),
                "url": kwargs["base_url"].format(**url),
                "debrid_provider": f"{item['source_title']} - {item['library_title']}",
                "provider_name_override": ADDON_IDS[self._scraper]["name"],
                "plugin": self._plugin,
            }
        )

        return source

    def __make_query(self, resource, query, **kwargs):
        result = self._api.search(resource, query, **kwargs) or []

        return result

    def _make_show_query(self, **kwargs):
        result = []
        for resource in self._resources:
            result.extend(
                [
                    dict(resource=resource, **i)
                    for i in self.__make_query(
                        resource, kwargs["simple_info"]["episode_title"], type="episode"
                    )
                ]
            )

        return result

    def _make_movie_query(self, **kwargs):
        result = []
        for resource in self._resources:
            result.extend(
                [
                    dict(resource=resource, **i)
                    for i in self.__make_query(
                        resource,
                        kwargs["title"],
                        year=kwargs["year"],
                        type="movie",
                    )
                ]
            )

        return result

    def _process_item(self, item, simple_info, all_info, type, **kwargs):
        try:
            item_type = item.get("type", "")
            resource = item.get("resource", ())
            media = item.get("Media", [{}])[0]
            meta_title = item.get("title", "")
            source_title = item.get("sourceTitle", "")
            library_title = item.get("librarySectionTitle", "")
            year = int(item.get("year", 0))

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

            size = common.convert_size(part.get("size", 0))
            file = part.get("file", "")
            key = part.get("key", "") if not self._plugin else item.get("key", "")
        except Exception as e:
            common.log(f"a4kOfficial: Failed to process Plex source: {e}", "error")
            return

        filename = file
        if "/" in file:
            filename = file.rsplit("/", 1)[-1]
        elif "\\" in file:
            filename = file.rsplit("\\", 1)[-1]

        if item_type != type:
            return

        item = {
            "filename": filename,
            "info": info,
            "size": size,
            "quality": quality,
            "source_title": source_title,
            "library_title": library_title,
        }
        url = {"base_url": resource[0], "token": resource[1]}

        if type == "movie":
            titles = [simple_info["title"], *simple_info.get("aliases", [])]
            if (
                year < int(simple_info["year"]) - 1
                or year > int(simple_info["year"]) + 1
            ):
                return
            elif not any(
                [clean_title(meta_title) != clean_title(title) for title in titles]
            ):
                return

            url.update({"movie_id": key})
            return self._make_movie_source(
                item,
                url,
                **kwargs,
            )
        elif type == "episode":
            show_title = item.get("grandparentTitle", "")
            episode_title = item.get("title", "")
            season = item.get("parentIndex", 0)
            episode = item.get("index", 0)
            titles = [simple_info["show_title"], *simple_info.get("show_aliases", [])]

            if not (
                season == simple_info["season_number"]
                and episode == simple_info["episode_number"]
            ):
                return
            elif not (
                any([clean_title(show_title) == clean_title(title) for title in titles])
                and clean_title(simple_info["episode_title"])
                == clean_title(episode_title)
            ):
                return

            url.update({"episode_id": key})
            return self._make_episode_source(item, url, **kwargs)

    @staticmethod
    def get_listitem(return_data):
        scraper = return_data["scraper"]
        if not configure.check_for_addon(ADDON_IDS[scraper]["plugin"]):
            common.log(
                f"a4kOfficial: '{ADDON_IDS[scraper]['plugin']}' is not installed; disabling '{scraper}'",
                "info",
            )
            configure.change_provider_status(scraper, "disabled")
        else:
            return super(PlexCore, PlexCore).get_listitem(return_data)
