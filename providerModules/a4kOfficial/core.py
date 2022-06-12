import xbmcgui

import time

from providerModules.a4kOfficial import common
from providerModules.a4kOfficial.common import ADDON_IDS
from providerModules.a4kOfficial.justwatch import JustWatch

from resources.lib.common.source_utils import clean_title
from resources.lib.modules.exceptions import PreemptiveCancellation


class Core:
    def __init__(self):
        self._country = common.get_setting("justwatch.country")
        self.start_time = 0
        self._scraper = self.__module__.split('.')[-1]
        self._monetization_types = ["free", "flatrate"]

        self._providers = None
        self._scheme = None
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

    def __make_query(self, query, type, **kwargs):
        items = self._api.search_for_item(
            query=clean_title(query),
            content_types=[type],
            providers=self._providers,
            monetization_types=self._monetization_types,
            **kwargs
        ).get("items")

        return items

    def _make_movie_query(self, title, year):
        items = self.__make_query(
            query=title,
            type="movie",
            release_year_from=int(year) - 1,
            release_year_until=int(year) + 1,
        )

        return items

    def _make_show_query(self, show_title):
        items = self.__make_query(query=show_title, type="show")

        return items

    def _process_item(
        self, provider, tmdb_id, type, season=0, episode=0, id_format=None
    ):
        source = None

        jw_title = self._api.get_title(title_id=provider['id'], content_type=type)
        external_ids = jw_title.get("external_ids", {})
        tmdb_ids = [i['external_id'] for i in external_ids if i['provider'] == 'tmdb']

        if len(tmdb_ids) >= 1 and int(tmdb_ids[0]) == tmdb_id:
            service_id = self._get_service_id(provider, season, episode)
            if not service_id:
                return None

            source = {
                "scraper": self._scraper,
                "video_id": service_id,
                "release_title": provider['title'],
                "quality": self._get_offered_resolutions(provider),
                "url": self._movie_url.format(
                    ADDON_IDS[self._scraper],
                    id_format(service_id) if id_format is not None else service_id,
                ),
            }

            if type == "show":
                s = self._api.get_season(jw_title['seasons'][season - 1]['id'])
                e = s['episodes'][episode - 1]
                episode_id = self._get_service_id(e, season, episode)
                if not episode_id:
                    return None

                service_ep_id = self._get_service_ep_id(service_id, season, episode, e)
                source.update(
                    {
                        "video_id": episode_id,
                        "release_title": e['title'],
                        "url": self._episode_url.format(
                            ADDON_IDS[self._scraper],
                            id_format(service_ep_id)
                            if id_format is not None
                            else service_ep_id,
                        ),
                    }
                )

        return source

    def _process_movie_item(self, provider, simple_info, all_info, id_format=None):
        source = self._process_item(
            provider, all_info['info']['tmdb_id'], "movie", id_format=id_format
        )
        return source

    def _process_show_item(self, provider, simple_info, all_info, id_format=None):
        source = self._process_item(
            provider,
            all_info['info']['tmdb_show_id'],
            "show",
            int(simple_info["season_number"]),
            int(simple_info["episode_number"]),
            id_format=id_format,
        )
        return source

    def _get_service_offers(self, item):
        offers = item["offers"]
        service_offers = [
            o
            for o in offers
            if o['package_short_name'] in self._providers
            and o['monetization_type'] in self._monetization_types
        ]

        return service_offers

    def _get_service_id(self, item, season, episode):
        service_offers = self._get_service_offers(item)
        if not service_offers:
            return None

        offer = service_offers[0]
        url = offer['urls'][self._scheme]
        id = url.rstrip('/').split('/')[-1]

        return id

    def _get_offered_resolutions(self, item):
        resolutions = set()
        service_offers = self._get_service_offers(item)
        if not service_offers:
            return None

        for offer in service_offers:
            resolutions.update(self._get_quality(offer))

        order = {key: i for i, key in enumerate(["4K", "1080p", "720p", "SD"])}

        return '/'.join(sorted(list(resolutions), key=lambda x: order[x]))

    def _get_service_ep_id(self, show_id, season, episode, item):
        return self._get_service_id(item=item)

    @staticmethod
    def _get_quality(offer):
        types = {
            "4K": ("4K",),
            "HD": (
                "1080p",
                "720p",
            ),
            "SD": ("SD",),
        }
        return types[offer["presentation_type"].upper()]

    def episode(self, simple_info, all_info, id_format=None):
        self.start_time = time.time()
        sources = []

        show_title = simple_info["show_title"]

        try:
            self._api = JustWatch(country=self._country)
            items = self._make_show_query(show_title)

            for item in items:
                source = self._process_show_item(
                    item, simple_info, all_info, id_format=None
                )
                if source is not None:
                    sources.append(source)
                    break
        except PreemptiveCancellation:
            return self._return_results("episode", sources, preemptive=True)

        return self._return_results("episode", sources)

    def movie(self, simple_info, all_info, id_format=None):
        self.start_time = time.time()
        sources = []
        queries = []
        queries.append(simple_info['title'])
        queries.extend(simple_info.get('aliases', []))

        try:
            self._api = JustWatch(country=self._country)
            items = []
            for query in queries:
                items.extend(self._make_movie_query(query, simple_info['year']))

            for item in items:
                source = self._process_movie_item(
                    item, simple_info, all_info, id_format
                )
                if source is not None:
                    sources.append(source)
                    break
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
