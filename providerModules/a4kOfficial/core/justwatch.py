# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

import xbmcaddon

from providerModules.a4kOfficial import ADDON_IDS, common, drm
from providerModules.a4kOfficial.core import Core
from providerModules.a4kOfficial.api.justwatch import JustWatch

from resources.lib.common.source_utils import clean_title


class JustWatchCore(Core):
    def __init__(self, providers, scheme="standard_web"):
        super(JustWatchCore, self).__init__()
        self._country = common.get_setting("justwatch.country")
        self._api = JustWatch(country=self._country)
        self._monetization_types = ["free", "flatrate"]
        self._plugin = ADDON_IDS[self._scraper]["plugin"]
        self._service_offers = []

        self._providers = providers
        self._scheme = scheme
        self._base_url = f"plugin://{self._plugin}"
        self._movie_url = self._base_url + "{movie_url}"
        self._episode_url = self._base_url + "{episode_url}"

    def _make_source(self, item, ids, **kwargs):
        source = super(JustWatchCore, self)._make_source(item, ids, **kwargs)
        source.update(
            {
                "release_title": item["title"],
                "quality": self._get_offered_resolutions(item),
                "info": self._get_info_from_settings(),
                "plugin": self._plugin,
                "debrid_provider": self._plugin,
                "provider_name_override": ADDON_IDS[self._scraper]["name"],
            }
        )

        base_url = kwargs["base_url"]
        source["url"] = base_url.format(**ids)

        return source

    def _get_info_from_settings(self):
        addon = xbmcaddon.Addon(self._plugin)
        info = set()
        settings = ADDON_IDS[self._scraper].get("settings", {})

        for setting in settings:
            if addon.getSettingBool(settings[setting]):
                info.add(setting)

        if drm.get_widevine_level() == "L3" or (
            "4K" in settings and not addon.getSettingBool(settings["4K"])
        ):
            info.difference_update({"HDR", "DV", "HYBRID"})

        return info

    def __make_query(self, query, type, **kwargs):
        items = self._api.search_for_item(
            query=clean_title(query),
            content_types=[type],
            providers=self._providers,
            monetization_types=self._monetization_types,
            **kwargs,
        ).get("items", [])

        return items

    def _make_movie_query(self, **kwargs):
        items = self.__make_query(
            query=kwargs["title"],
            type="movie",
            release_year_from=int(kwargs["year"]) - 1,
            release_year_until=int(kwargs["year"]) + 1,
        )

        return items

    def _make_show_query(self, **kwargs):
        items = self.__make_query(
            query=kwargs["simple_info"]["show_title"], type="show"
        )

        return items

    def _process_item(self, item, simple_info, all_info, type, **kwargs):
        source = None
        if not self._get_service_offers(item):
            return None

        jw_title = self._api.get_title(title_id=item["id"], content_type=type)
        external_ids = jw_title.get("external_ids", {})
        tmdb_ids = [i["external_id"] for i in external_ids if i["provider"] == "tmdb"]

        tmdb_id = all_info["info"].get(
            "tmdb_show_id" if type == "episode" else "tmdb_id"
        )
        season = int(simple_info.get("season_number", 0))
        episode = int(simple_info.get("episode_number", 0))
        if len(tmdb_ids) >= 1 and int(tmdb_ids[0]) == tmdb_id:
            service_id = self._get_service_id(item, season, episode)
            if not service_id:
                return None

            source = self._make_movie_source(item, {"movie_id": service_id}, **kwargs)

            if type == "episode":
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

                source = self._make_episode_source(episode_item, ids, **kwargs)

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

        settings = ADDON_IDS[self._scraper].get("settings", {})

        if drm.get_widevine_level() == "L3" or (
            "4K" in settings
            and not xbmcaddon.Addon(self._plugin).getSettingBool(settings["4K"])
        ):
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

    def episode(self, simple_info, all_info, **kwargs):
        return super(JustWatchCore, self).episode(
            simple_info, all_info, single=True, **kwargs
        )

    def movie(self, simple_info, all_info, **kwargs):
        return super(JustWatchCore, self).movie(
            simple_info, all_info, single=True, **kwargs
        )

    @staticmethod
    def get_listitem(return_data):
        scraper = return_data["scraper"]
        plugin = ADDON_IDS[scraper]["plugin"]
        if not common.check_for_addon(plugin):
            common.log(
                f"a4kOfficial: '{plugin}' is not installed; disabling '{scraper}'",
                "info",
            )
            common.change_provider_status(scraper, "disabled")
        else:
            return super(JustWatchCore, JustWatchCore).get_listitem(return_data)
