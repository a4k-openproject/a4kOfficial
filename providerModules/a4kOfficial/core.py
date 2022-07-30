# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

import time

import xbmcgui

from providerModules.a4kOfficial import common

from resources.lib.modules.exceptions import PreemptiveCancellation


class Core:
    def __init__(self):
        self.start_time = time.time()
        self.sources = []
        self._scraper = self.__module__.split('.')[-1]

    def _return_results(self, source_type, sources, preemptive=False):
        if preemptive:
            common.log(
                "a4kOfficial.{}.{}: cancellation requested".format(
                    source_type, self._scraper
                ),
                "info",
            )
        common.log(
            "a4kOfficial.{}.{}: {}".format(source_type, self._scraper, len(sources)),
            "info",
        )
        common.log(
            "a4kOfficial.{}.{}: took {} ms".format(
                source_type, self._scraper, int((time.time() - self.start_time) * 1000)
            ),
            "info",
        )

        return sources

    def episode(self, simple_info, all_info):
        try:
            items = self._make_show_query()

            for item in items:
                source = self._process_show_item(item, all_info)
                if source is not None:
                    self.sources.append(source)
                    break
        except PreemptiveCancellation:
            return self._return_results("episode", self.sources, preemptive=True)

        return self._return_results("episode", self.sources)

    def movie(self, simple_info, all_info):
        queries = []
        queries.append(simple_info['title'])
        queries.extend(simple_info.get('aliases', []))

        try:
            items = []
            for query in queries:
                items.extend(self._make_movie_query(query, int(simple_info['year'])))

            for item in items:
                source = self._process_movie_item(item, all_info)
                if source is not None:
                    self.sources.append(source)
                    break
        except PreemptiveCancellation:
            return self._return_results("movie", self.sources, preemptive=True)

        return self._return_results("movie", self.sources)

    @staticmethod
    def get_listitem(return_data):
        list_item = xbmcgui.ListItem(path=return_data["url"], offscreen=True)
        list_item.setContentLookup(False)
        list_item.setProperty('isFolder', 'false')
        list_item.setProperty('isPlayable', 'true')

        return list_item
