import xbmcgui

import re
import time

import requests

from providerModules.a4kOfficial import common
from providerModules.a4kOfficial.justwatch import JustWatch

from resources.lib.modules.exceptions import PreemptiveCancellation


class Core:
    def __init__(self):
        self._country = common.get_setting("justwatch.country")
        self.start_time = 0
        self._providers = None
        self._scraper = None
        self._service = None
        self._scheme = "standard_web"
        self._movie_url = None
        self._episode_url = None

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

    def _make_movie_query(self, title, year):
        items = self._api.search_for_item(
            query=title,
            content_types=["movie"],
            release_year_from=int(year) - 1,
            release_year_until=int(year) + 1,
            providers=self._providers,
        ).get("items")

        return items

    def _make_show_query(self, query):
        items = self._api.search_for_item(
            query=query, content_types=["show"], providers=self._providers
        ).get("items")

        return items

    def _process_movie_item(self, provider, all_info):
        source = None
        scoring = provider.get("scoring", {})
        tmdb_id = [i['value'] for i in scoring if i['provider_type'] == 'tmdb:id']

        if len(tmdb_id) == 1 and tmdb_id[0] == all_info['info']['tmdb_id']:
            service_id = self._get_service_id(provider)
            if not service_id:
                return None

            source = {
                "scraper": self._scraper,
                "release_title": provider['title'],
                "info": "",
                "size": 0,
                "quality": "Variable",
                "url": self._movie_url.format(service_id),
            }

        return source

    def _process_show_item(self, provider, show_id, season, episode):
        source = None

        jw_title = self._api.get_title(title_id=provider['id'], content_type="show")
        external_ids = jw_title.get("external_ids", {})
        tmdb_id = [i['external_id'] for i in external_ids if i['provider'] == 'tmdb']

        if len(tmdb_id) >= 1 and int(tmdb_id[0]) == show_id:
            show_id = self._get_service_id(provider)
            if not show_id:
                return None

            s = self._api.get_season(jw_title['seasons'][season - 1]['id'])
            e = s['episodes'][episode - 1]
            episode_id = self._get_service_id(e)
            if not episode_id:
                return None

            source = {
                "scraper": self._scraper,
                "release_title": e['title'],
                "info": "",
                "quality": "Variable",
                "size": 0,
                "url": self._episode_url.format(
                    self._get_service_ep_id(show_id, season, episode, e)
                ),
            }

        return source

    def _get_service_id(self, item):
        offers = item["offers"]
        service_offers = [
            o for o in offers if o['package_short_name'] in self._providers
        ]
        if not service_offers:
            return None

        offer = service_offers[0]
        url = offer['urls'][self._scheme]
        id = url.rstrip('/').split('/')[-1]

        return id

    def _get_service_ep_id(self, show_id, season, episode, item):
        countryDict = {
            'AR': '21',
            'AU': '23',
            'BE': '26',
            'BR': '29',
            'CA': '33',
            'CO': '36',
            'CZ': '307',
            'FR': '45',
            'DE': '39',
            'GR': '327',
            'HK': '331',
            'HU': '334',
            'IS': '265',
            'IN': '337',
            'IL': '336',
            'IT': '269',
            'JP': '267',
            'LT': '357',
            'MY': '378',
            'MX': '65',
            'NL': '67',
            'PL': '392',
            'PT': '268',
            'RU': '402',
            'SG': '408',
            'SK': '412',
            'ZA': '447',
            'KR': '348',
            'ES': '270',
            'SE': '73',
            'CH': '34',
            'TH': '425',
            'TR': '432',
            'GB': '46',
            'US': '78',
        }

        code = countryDict.get(self._country, '78')
        url = "https://www.instantwatcher.com/{}/{}/title/{}".format(
            self._service, code, show_id
        )
        r = requests.get(url, timeout=10).text
        r = common.parseDOM(r, 'div', attrs={'class': 'tdChildren-titles'})[0]
        seasons = re.findall(
            r'(<div class="iw-title netflix-title list-title".+?<div class="grandchildren-titles"></div></div>)',
            r,
            flags=re.I | re.S,
        )
        _season = [
            s
            for s in seasons
            if int(re.findall(r'>Season (.+?)</a>', s, flags=re.I | re.S)[0]) == season
        ][0]
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
            items = self._make_movie_query(
                simple_info['title'].lower(), simple_info['year']
            )

            for item in items:
                source = self._process_movie_item(item, all_info)
                if source is not None:
                    sources.append(source)
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
