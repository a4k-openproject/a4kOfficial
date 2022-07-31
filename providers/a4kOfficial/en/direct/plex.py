# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

from providerModules.a4kOfficial import common
from providerModules.a4kOfficial.core import Core
from providerModules.a4kOfficial.api.plex import Plex

from resources.lib.modules.exceptions import PreemptiveCancellation
from resources.lib.common.source_utils import (
    check_episode_number_match,
    check_title_match,
    clean_title,
    get_info,
    get_quality,
    de_string_size,
)


PLEX_AUDIO = {'dca': 'dts', 'dca-ma': 'hdma'}
_api = Plex()


def setup():
    success = _api.auth()
    for setting in ["plex.token", "plex.client_id", "plex.device_id"]:
        common.log(common.get_setting(setting))

    return success


class sources(Core):
    def __init__(self):
        super(sources, self).__init__()
        self._api = Plex()
        self._resources = self._api.get_resources()

    def __make_query(self, resource, query, **kwargs):
        result = self._api.search(resource, query, **kwargs)

        return result

    def _make_show_query(self, resource, show_title):
        result = {}

        return result.get("tvshows", {})

    def _make_movie_query(self, resource, title, year):
        result = self.__make_query(resource, title, year=year, type="movie")

        if result == None:
            return []

        return result.findall("Video")

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
            media = item.find("Media")
            year = int(media.get("year", simple_info["year"]))
            source_title = item.get("sourceTitle", "")
            quality = media.get("videoResolution", "Unknown")
            part = media.find("Part")
            size = str(int(part.get("size", 0)) / 1024 / 1024) + "MiB"
            key = part.get("key", "")
            file = part.get("file", "")
            info = ' '.join(
                [
                    media.get("audioChannels", "2") + "ch",
                    media.get("videoCodec"),
                    PLEX_AUDIO.get(media.get("audioCodec"), media.get("audioCodec")),
                    media.get("audioProfile"),
                    media.get("container"),
                ]
            )
        except Exception as e:
            common.log(
                "a4kOfficial: Failed to process Plex source: {}".format(e), "error"
            )
            return

        filename = file.split('/')[-1]
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

        source = {
            "scraper": self._scraper,
            "release_title": filename,
            "info": get_info(filename).union(get_info(info)),
            "size": de_string_size(size),
            "quality": get_quality(quality),
            "url": "{}{}?X-Plex-Client-Identifier={}&X-Plex-Token={}".format(
                resource[0],
                key,
                common.get_setting("plex.client_id"),
                resource[1],
            ),
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
