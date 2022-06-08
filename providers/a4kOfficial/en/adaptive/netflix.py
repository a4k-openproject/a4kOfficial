# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

import xbmcgui

import re
import time

import requests

from providerModules.a4kOfficial import common
from providerModules.a4kOfficial.justwatchapi import JustWatch

from resources.lib.modules.exceptions import PreemptiveCancellation


class sources:
    def __init__(self):
        self._country = common.get_setting("justwatch.country")
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

    def _make_movie_query(self, title, year):
        items = self._api.search_for_item(
            query=title,
            content_types=["movie"],
            release_year_from=int(year) - 1,
            release_year_until=int(year) + 1,
            providers=["nfx", "nff", "nfk"]
        ).get("items")

        return items

    def _make_show_query(self, query):
        items = self._api.search_for_item(
            query=query,
            content_types=["show"],
            providers=["nfx", "nff", "nfk"]
        ).get("items")

        return items

    def _process_movie_item(self, provider, all_info):
        source = None
        scoring = provider.get("scoring", {})
        tmdb_id = [i['value'] for i in scoring if i['provider_type'] == 'tmdb:id']
        
        if len(tmdb_id) == 1 and tmdb_id[0] == all_info['info']['tmdb_id']:
            netflix_id = self._get_netflix_id(provider)
            
            source = {"scraper": "netflix",
                    "release_title": provider['title'],
                    "info": "",
                    "size": 0,
                    "url": "plugin://plugin.video.netflix/play_strm/{}/".format(
                        netflix_id
                    )}
            if len(netflix_offers) == 1:
                source['quality'] = self._get_quality(offer)
            elif len(netflix_offers) > 1:
                source['quality'] = "Variable"

        return source

    def _process_show_item(self, provider, show_id, season, episode):
        source = None
        
        jw_title = self._api.get_title(title_id=provider['id'], content_type="show")
        external_ids = jw_title.get("external_ids", {})
        tmdb_id = [i['external_id'] for i in external_ids if i['provider'] == 'tmdb']
        
        if len(tmdb_id) >= 1 and int(tmdb_id[0]) == show_id:
            show_id = self._get_netflix_id(provider)
            if not show_id:
                return None
            
            s = self._api.get_season(jw_title['seasons'][season - 1]['id'])
            e = s['episodes'][episode - 1]
            episode_id = self._get_netflix_id(e)
            if not episode_id:
                return None
            
            source = {"scraper": "netflix",
                    "release_title": e['title'],
                    "info": "",
                    "quality": "Variable",
                    "size": 0,
                    "url": "plugin://plugin.video.netflix/play_strm/{}/".format(
                        self._get_nf_ep_id(show_id, season, episode)
                    )}

        return source

    @staticmethod
    def _get_netflix_id(item):
        offers = item["offers"]
        if not offers:
            return None
        
        offer = offers[0]
        url = offer['urls']['standard_web']
        netflix_id = url.rstrip('/').split('/')[-1]
        
        return netflix_id

    def _get_nf_ep_id(self, show_id, season, episode):
        countryDict = {'AR': '21', 'AU': '23', 'BE': '26', 'BR': '29', 'CA': '33', 'CO': '36', 'CZ': '307', 'FR': '45', 'DE': '39', 'GR': '327', 'HK': '331', 'HU': '334',
                           'IS': '265', 'IN': '337', 'IL': '336', 'IT': '269', 'JP': '267', 'LT': '357', 'MY': '378', 'MX': '65', 'NL': '67', 'PL': '392', 'PT': '268', 'RU': '402',
                           'SG': '408', 'SK': '412', 'ZA': '447', 'KR': '348', 'ES': '270', 'SE': '73', 'CH': '34', 'TH': '425', 'TR': '432', 'GB': '46', 'US': '78'}

        code = countryDict.get(self._country, '78')
        url = 'https://www.instantwatcher.com/netflix/%s/title/%s' % (code, show_id)
        r = requests.get(url, timeout=10).text
        r = common.parseDOM(r, 'div', attrs={'class': 'tdChildren-titles'})[0]
        seasons = re.findall(r'(<div class="iw-title netflix-title list-title".+?<div class="grandchildren-titles"></div></div>)', r, flags=re.I|re.S)
        _season = [s for s in seasons if int(re.findall(r'>Season (.+?)</a>', s, flags=re.I|re.S)[0]) == season][0]
        episodes = common.parseDOM(_season, 'a', ret='data-title-id')
        episode_id = episodes[int(episode)]

        return episode_id

    @staticmethod
    def _get_quality(offer):
        types = {"4K": "4K", "HD": "1080p", "SD": "SD"}
        return types[offer["presentation_type"].upper()]

    def episode(self, simple_info, all_info):
        self.start_time = time.time()
        sources = []

        show_title = simple_info["show_title"]
        show_id = all_info['info']['tmdb_show_id']
        season = simple_info["season_number"]
        episode = simple_info["episode_number"]
        
        try:
            self._api = JustWatch(country=self._country)
            items = self._make_show_query(show_title.lower())
            
            for item in items:
                source = self._process_show_item(
                    item, show_id, int(season), int(episode)
                )
                if source is not None:
                    sources.append(source)
        except PreemptiveCancellation:
            return self._return_results("episode", sources, preemptive=True)

        return self._return_results("episode", sources)

    def movie(self, simple_info, all_info):
        self.start_time = time.time()
        sources = []

        try:
            self._api = JustWatch(country=self._country)
            items = self._make_movie_query(simple_info['title'].lower(), simple_info['year'])
            
            for item in items:
                nf_source = self._process_movie_item(item, all_info)
                if nf_source is not None:
                    sources.append(nf_source)
        except PreemptiveCancellation:
            return self._return_results("movie", sources, preemptive=True)
        
        return self._return_results("movie", sources)

    @staticmethod
    def get_listitem(return_data):
        list_item = xbmcgui.ListItem(path=return_data["url"], offscreen=True)
        list_item.setContentLookup(False)
        list_item.setProperty('isFolder', 'false')
        list_item.setProperty('isPlayable', 'true')

        return list_item
