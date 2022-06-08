# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

import xbmcgui

import time

from providerModules.a4kOfficial import common
from providerModules.a4kOfficial.justwatchapi import JustWatch

from resources.lib.modules.exceptions import PreemptiveCancellation


class sources:
    def __init__(self):
        self._country = common.get_setting("justwatch.country")
        self._api = JustWatch(country=self._country)
        self.start_time = 0

    def _return_results(self, source_type, sources, preemptive=False):
        if preemptive:
            common.log(
                "a4kOfficial.{}.netflix: cancellation requested".format(source_type),
                "info",
            )
        common.log(
            "a4kOfficial.{}.netflix: {}".format(source_type, len(sources)), "info"
        )
        common.log(
            "a4kOfficial.{}.netflix: took {} ms".format(
                source_type, int((time.time() - self.start_time) * 1000)
            ),
            "info",
        )
        return sources

    def _make_query(self, query, year):
        items = self._api.search_for_item(
            query=query,
            content_types=["movie"],
            release_year_from=int(year) - 1,
            release_year_until=int(year) + 1,
        ).get("items")

        return items

    def _process_item(self, provider, all_info):
        sources = []
        scoring = provider.get("scoring", {})
        tmdb_id = [i['value'] for i in scoring if i['provider_type'] == 'tmdb:id']
        
        if len(tmdb_id) == 1 and tmdb_id[0] == all_info['info']['tmdb_id']:
            offers = provider['offers']
            netflix_offers = [o for o in offers if o['package_short_name'] == 'nfx']
            for offer in netflix_offers:
                url = offer['urls']['standard_web']
                netflix_id = url.rstrip('/').split('/')[-1]

                source = {
                    "scraper": "netflix",
                    "release_title": provider['title'],
                    "info": "",
                    "size": 0,
                    "quality": self._get_quality(offer),
                    "url": "plugin://plugin.video.netflix/play_strm/{}/".format(
                        netflix_id
                    ),
                }
                sources.append(source)

        return sources

    @staticmethod
    def _get_quality(offer):
        types = {"4K": "4K", "HD": "1080p", "SD": "SD"}
        return types[offer["presentation_type"].upper()]

    def episode(self, simple_info, all_info):
        self.start_time = time.time()
        sources = []
        if not self.auth:
            return sources

        show_title = simple_info["show_title"]
        season_x = simple_info["season_number"]
        season_xx = season_x.zfill(2)
        episode_x = simple_info["episode_number"]
        episode_xx = episode_x.zfill(2)
        absolute_number = simple_info["absolute_number"]
        is_anime = simple_info["isanime"]

        numbers = [(season_x, episode_x), (season_xx, episode_xx), absolute_number]

        queries = []
        if is_anime and absolute_number:
            queries.append("\"{}\" {}".format(show_title, numbers[2]))
        else:
            for n in numbers[:2]:
                queries.append("\"{}\" S{}E{}".format(show_title, n[0], n[1]))

        for query in queries:
            try:
                down_url, dl_farm, dl_port, files = self._make_query(query)
            except PreemptiveCancellation:
                return self._return_results("episode", sources, preemptive=True)

            for item in files:
                source = self._process_item(
                    item, down_url, dl_farm, dl_port, simple_info
                )
                if source is not None:
                    sources.append(source)

        return self._return_results("episode", sources)

    def movie(self, simple_info, all_info):
        self.start_time = time.time()
        sources = []

        try:
            items = self._make_query(simple_info['title'].lower(), simple_info['year'])
        except PreemptiveCancellation:
            return self._return_results("movie", sources, preemptive=True)
        
        for item in items:
            nf_sources = self._process_item(item, all_info)
            sources.extend(nf_sources)
        
        return self._return_results("movie", sources)

    @staticmethod
    def get_listitem(return_data):
        list_item = xbmcgui.ListItem(path=return_data["url"], offscreen=True)
        list_item.setContentLookup(False)
        list_item.setProperty('isFolder', 'false')
        list_item.setProperty('isPlayable', 'true')

        return list_item
