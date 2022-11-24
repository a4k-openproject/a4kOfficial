# -*- coding: utf-8 -*-
import xbmcaddon

from resources.lib.common.source_utils import clean_title
from resources.lib.modules.exceptions import PreemptiveCancellation

from providerModules.a4kOfficial import ADDON_IDS, common, drm
from providerModules.a4kOfficial.core import Core
from providerModules.a4kOfficial.api.justwatch import JustWatch


class JustWatchCore(Core):
    def __init__(self, providers, scheme="standard_web"):
        super().__init__()
        self._country = common.get_setting("justwatch.country")

        try:
            self._api = JustWatch(country=self._country)
        except PreemptiveCancellation:
            self._api = None

        self._monetization_types = ["free", "flatrate"]
        self._plugin = ADDON_IDS[self._scraper]["plugin"]
        self._service_offers = []

        self._providers = providers
        self._scheme = scheme
        self._base_url = f"plugin://{self._plugin}"
        self._movie_url = self._base_url + "{movie_url}"
        self._episode_url = self._base_url + "{episode_url}"

    @staticmethod
    def _make_release_title(item, simple_info, info, type):
        if type == "movie":
            return simple_info['title']
        elif type == "episode":
            return f"{simple_info['show_title']}: \
                     S{int(simple_info['season_number']):02}E{int(simple_info['season_number']):02} - \
                     {simple_info['episode_title']}"
        else:
            return item['title']

    def _make_source(self, item, ids, simple_info, info, **kwargs):
        source = super()._make_source(item, ids, simple_info, info, **kwargs)
        source.update(
            {
                "release_title": JustWatchCore._make_release_title(item, simple_info, info, kwargs["type"]),
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

        if drm.get_widevine_level() == "L3" or ("4K" in settings and not addon.getSettingBool(settings["4K"])):
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
        items = self.__make_query(query=kwargs["simple_info"]["show_title"], type="show")

        return items

    def _process_item(self, item, simple_info, info, type, **kwargs):
        source = None
        if not self._get_service_offers(item):
            return None

        jw_title = self._api.get_title(title_id=item["id"], content_type="show" if type == "episode" else type)
        external_ids = jw_title.get("external_ids", {})
        tmdb_ids = [i["external_id"] for i in external_ids if i["provider"] == "tmdb"]

        tmdb_id = info["info"].get("tmdb_show_id" if type == "episode" else "tmdb_id")
        season = int(simple_info.get("season_number", 0))
        episode = int(simple_info.get("episode_number", 0))
        if len(tmdb_ids) >= 1 and int(tmdb_ids[0]) == tmdb_id:
            service_id = self._get_service_id(item, season, episode)
            if not service_id:
                return None

            source = self._make_movie_source(item, {"movie_id": service_id}, simple_info, info, **kwargs)

            if type == "episode":
                episodes = self._api.get_episodes(item["id"])["items"]
                episode_item = [
                    i for i in episodes if i["season_number"] == int(season) and i["episode_number"] == int(episode)
                ]

                if not episode_item:
                    return None
                episode_item = episode_item[0]
                ids = {"show_id": service_id}
                ids.update(self._get_service_ep_id(service_id, episode_item, season, episode))

                if not ids.get("episode_id"):
                    return None

                source = self._make_episode_source(episode_item, ids, simple_info, info, **kwargs)

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
            if o.get("package_short_name") in self._providers and o.get("monetization_type") in self._monetization_types
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

        try:
            if drm.get_widevine_level() == "L3" or (
                "4K" in settings and not xbmcaddon.Addon(self._plugin).getSettingBool(settings["4K"])
            ):
                resolutions.discard("4K")
        except Exception:
            common.log(f"Could not identify WV capabilities from {self._plugin}", "error")

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

    def episode(self, simple_info, info, **kwargs):
        return super().episode(simple_info, info, single=True, **kwargs)

    def movie(self, title, year, imdb, simple_info, info, **kwargs):
        return super().movie(title, year, imdb, simple_info, info, single=True, **kwargs)

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
