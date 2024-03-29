# -*- coding: utf-8 -*-
import time

import xbmcgui

from resources.lib.modules.exceptions import PreemptiveCancellation

from providerModules.a4kOfficial import common


class Core:
    def __init__(self):
        self.start_time = time.time()
        self.sources = []
        self._scraper = self.__module__.split(".")[-1]

    def _return_results(self, source_type, sources, preemptive=False, extra=None):
        if preemptive:
            common.log(
                f"a4kOfficial.{source_type}.{self._scraper}: cancellation requested",
                "info",
            )
        if extra:
            common.log(f"a4kOfficial.{source_type}.{self._scraper}: {extra}", "info")
        common.log(
            f"a4kOfficial.{source_type}.{self._scraper}: {len(sources)}",
            "info",
        )
        common.log(
            f"a4kOfficial.{source_type}.{self._scraper}: took {int((time.time() - self.start_time) * 1000)} ms",
            "info",
        )
        common.log(
            f"a4kOfficial.{source_type}.{self._scraper}: {sources}",
            "debug",
        )

        return sources

    def _make_source(self, item, ids, simple_info, info, **kwargs):
        source = {
            "scraper": self._scraper,
        }
        source.update(ids)

        return source

    def _make_episode_source(self, item, ids, simple_info, info, **kwargs):
        return self._make_source(item, ids, simple_info, info, base_url=self._episode_url, type="episode", **kwargs)

    def _make_movie_source(self, item, ids, simple_info, info, **kwargs):
        return self._make_source(item, ids, simple_info, info, base_url=self._movie_url, type="movie", **kwargs)

    def _process_movie_item(self, item, simple_info, info, **kwargs):
        source = self._process_item(item, simple_info, info, type="movie", **kwargs)
        return source

    def _process_show_item(self, item, simple_info, info, **kwargs):
        source = self._process_item(
            item,
            simple_info,
            info,
            type="episode",
            **kwargs,
        )
        return source

    def episode(self, simple_info, info, **kwargs):
        if self._api is None:
            return self._return_results("episode", [])

        try:
            items = self._make_show_query(simple_info=simple_info)

            for item in items:
                source = self._process_show_item(item, simple_info, info, **kwargs)
                if source is not None:
                    self.sources.append(source)
                if kwargs.get("single"):
                    break
        except PreemptiveCancellation:
            return self._return_results("episode", self.sources, preemptive=True)
        except Exception as e:
            return self._return_results("episode", self.sources, extra=e)
        else:
            return self._return_results("episode", self.sources)

    def movie(self, title, year, imdb, simple_info, info, **kwargs):
        if self._api is None:
            return self._return_results("movie", [])

        try:
            items = self._make_movie_query(title=simple_info["title"], year=int(simple_info["year"]))

            for item in items:
                source = self._process_movie_item(item, simple_info, info, **kwargs)
                if source is not None:
                    self.sources.append(source)
                if kwargs.get("single"):
                    break
        except PreemptiveCancellation:
            return self._return_results("movie", self.sources, preemptive=True)
        except Exception as e:
            return self._return_results("episode", self.sources, extra=e)
        else:
            return self._return_results("movie", self.sources)

    @staticmethod
    def get_listitem(return_data):
        list_item = xbmcgui.ListItem(path=return_data["url"], offscreen=True)
        list_item.setContentLookup(False)
        list_item.setProperty("isFolder", "false")
        list_item.setProperty("isPlayable", "true")

        return list_item
