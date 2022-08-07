# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

import requests

from providers.a4kOfficial import configure
from providerModules.a4kOfficial import ADDON_IDS, common, drm
from providerModules.a4kOfficial.core import Core
from providerModules.a4kOfficial.api.justwatch import JustWatch

from resources.lib.common.source_utils import clean_title
from resources.lib.modules.exceptions import PreemptiveCancellation


class JustWatchCore(Core):
    def __init__(self, providers, scheme="standard_web"):
        super(JustWatchCore, self).__init__()
        self._country = configure.get_setting("justwatch.country")
        self._monetization_types = ["free", "flatrate"]
        self._plugin = ADDON_IDS[self._scraper]["plugin"]
        self._service_offers = []

        self._providers = providers
        self._scheme = scheme
        self._base_url = f"plugin://{self._plugin}"
        self._movie_url = self._base_url + "{movie_url}"
        self._episode_url = self._base_url + "{episode_url}"

    def _make_source(self, item, ids, base_url, id_format=None):
        source = {
            "scraper": self._scraper,
            "plugin": self._plugin,
            "release_title": item["title"],
            "quality": self._get_offered_resolutions(item),
            "debrid_provider": self._plugin,
        }
        source.update(ids)
        source["url"] = base_url.format(
            **(
                {k: id_format(v) for k, v in ids.items()}
                if id_format is not None
                else ids
            )
        )

        return source

    def _make_episode_source(self, item, ids, id_format=None):
        return self._make_source(item, ids, self._episode_url, id_format)

    def _make_movie_source(self, item, ids, id_format=None):
        return self._make_source(item, ids, self._movie_url, id_format)

    def __make_query(self, query, type, **kwargs):
        items = self._api.search_for_item(
            query=clean_title(query),
            content_types=[type],
            providers=self._providers,
            monetization_types=self._monetization_types,
            **kwargs,
        ).get("items", [])

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

    def __process_item(self, item, tmdb_id, type, season=0, episode=0, id_format=None):
        source = None
        if not self._get_service_offers(item):
            return None

        jw_title = self._api.get_title(title_id=item["id"], content_type=type)
        external_ids = jw_title.get("external_ids", {})
        tmdb_ids = [i["external_id"] for i in external_ids if i["provider"] == "tmdb"]

        if len(tmdb_ids) >= 1 and int(tmdb_ids[0]) == tmdb_id:
            service_id = self._get_service_id(item, season, episode)
            if not service_id:
                return None

            source = self._make_movie_source(item, {"movie_id": service_id}, id_format)

            if type == "show":
                episodes = self._api.get_episodes(item["id"])["items"]
                episode_item = [
                    i
                    for i in episodes
                    if i["season_number"] == int(season)
                    and i["episode_number"] == int(episode)
                ]

                if not episode_item:
                    return None
                episode_item = episode_item[0]
                ids = {"show_id": service_id}
                ids.update(
                    self._get_service_ep_id(service_id, episode_item, season, episode)
                )

                if not ids.get("episode_id"):
                    return None

                source = self._make_episode_source(episode_item, ids, id_format)

        return source

    def _process_movie_item(self, item, simple_info, all_info, id_format=None):
        source = self.__process_item(
            item, all_info["info"]["tmdb_id"], "movie", id_format=id_format
        )
        return source

    def _process_show_item(self, item, simple_info, all_info, id_format=None):
        source = self.__process_item(
            item,
            all_info["info"]["tmdb_show_id"],
            "show",
            int(simple_info["season_number"]),
            int(simple_info["episode_number"]),
            id_format=id_format,
        )
        return source

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

    def _get_service_offers(self, item, offers=None):
        offers = offers or item.get("offers", [])
        service_offers = [
            o
            for o in offers
            if o.get("package_short_name") in self._providers
            and o.get("monetization_type") in self._monetization_types
        ]
        self._service_offers.extend(service_offers)

        return service_offers

    def _get_offered_resolutions(self, item):
        if not self._service_offers:
            return None

        resolutions = set()
        for offer in self._service_offers:
            resolutions.update(self._get_quality(offer))
        if drm.get_widevine_level() == "L3":
            resolutions.discard("4K")

        order = {key: i for i, key in enumerate(["4K", "1080p", "720p", "SD"])}

        return "/".join(sorted(list(resolutions), key=lambda x: order[x]))

    def _get_service_id(self, item, season=0, episode=0):
        if not self._service_offers:
            return None

        offer = self._service_offers[0]
        url = offer.get("urls", {}).get(self._scheme, "")
        if not common.check_url(url):
            return None

        id = url.rstrip("/").split("/")[-1]

        return id

    def _get_service_ep_id(self, show_id, item, season, episode):
        return {"episode_id": self._get_service_id(item)}

    def episode(self, simple_info, all_info, id_format=None):
        show_title = simple_info["show_title"]

        try:
            self._api = JustWatch(country=self._country)
            items = self._make_show_query(show_title)

            for item in items:
                source = self._process_show_item(
                    item, simple_info, all_info, id_format=None
                )
                if source is not None:
                    self.sources.append(source)
                    break
        except PreemptiveCancellation:
            return self._return_results("episode", self.sources, preemptive=True)

        return self._return_results("episode", self.sources)

    def movie(self, simple_info, all_info, id_format=None):
        queries = []
        queries.append(simple_info["title"])
        queries.extend(simple_info.get("aliases", []))

        try:
            self._api = JustWatch(country=self._country)
            items = []
            for query in queries:
                items.extend(self._make_movie_query(query, simple_info["year"]))

            for item in items:
                source = self._process_movie_item(
                    item, simple_info, all_info, id_format
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
        plugin = ADDON_IDS[scraper]["plugin"]
        if not configure.check_for_addon(plugin):
            common.log(
                f"a4kOfficial: '{plugin}' is not installed; disabling '{scraper}'",
                "info",
            )
            configure.change_provider_status(scraper, "disabled")
        else:
            return super(JustWatchCore, JustWatchCore).get_listitem(return_data)
