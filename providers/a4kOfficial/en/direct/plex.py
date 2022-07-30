# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

from providerModules.a4kOfficial import common
from providerModules.a4kOfficial.core import Core
from providerModules.a4kOfficial.api.plex import Plex

from resources.lib.modules.exceptions import PreemptiveCancellation

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

    def __make_query(self, base_url, query, **kwargs):
        result = self._api.search(base_url, query, **kwargs)

        return result

    def _make_show_query(self, base_url, show_title):
        result = {}

        return result.get("tvshows", {})

    def _make_movie_query(self, base_url, title, year):
        result = self.__make_query(base_url, title, year=year, type="movie")

        return result.findall("Video")

    def _process_show_item(self, base_url, item, all_info):
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

    def _process_movie_item(self, base_url, item, all_info):
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
        for url in self._resources:
            queries = []
            queries.append(simple_info['title'])
            queries.extend(simple_info.get('aliases', []))

            try:
                items = []
                for query in queries:
                    items.extend(
                        self._make_movie_query(url, query, int(simple_info['year']))
                    )

                for item in items:
                    source = self._process_movie_item(url, item, all_info)
                    if source is not None:
                        self.sources.append(source)
                        break
            except PreemptiveCancellation:
                return self._return_results("movie", self.sources, preemptive=True)

        return self._return_results("movie", self.sources)
