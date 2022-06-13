import xbmcaddon
import xbmcgui

import time

from providerModules.a4kOfficial import common
from providerModules.a4kOfficial.core import Core

from resources.lib.common.source_utils import clean_title, de_string_size
from resources.lib.modules.exceptions import PreemptiveCancellation


def get_quality(width):
    if width >= 2160:
        return "4K"
    elif width >= 1920:
        return "1080p"
    elif width >= 1280:
        return "720p"
    elif width < 1280:
        return "SD"


def get_file_info(db_details):
    file_info = {}
    filename = db_details.get("file", "")
    if not filename:
        return {}

    size = (
        common.execute_jsonrpc(
            method="Files.GetFileDetails",
            params={"file": filename, "media": "video", "properties": ["size"]},
        )
        .get("result", {})
        .get("filedetails", {})
        .get("size", 0)
    )
    file_info['size'] = de_string_size(common.convert_size(size))

    stream_details = db_details.get("streamdetails", {})
    audio_details = stream_details.get("audio", [{}])[0]
    video_details = stream_details.get("video", [{}])[0]

    file_info['info'] = set()
    if audio_channels := audio_details.get("channels"):
        file_info['info'].add("{}ch".format(audio_channels))
    if audio_codec := audio_details.get("codec"):
        file_info['info'].add("dts" if audio_codec == "dca" else audio_codec)
    if video_codec := video_details.get("codec"):
        file_info['info'].add("h264" if video_codec == "avc1" else video_codec)
    if video_codec := video_details.get("stereomode"):
        file_info['info'].add("3D")

    file_info['quality'] = get_quality(video_details.get("width", 0))

    return file_info


class LibraryCore(Core):
    def __init__(self):
        super(LibraryCore, self).__init__()

    def __make_query(self, method, params, **kwargs):
        result = common.execute_jsonrpc(method=method, params=params, **kwargs).get(
            "result", {}
        )

        return result

    def _make_movie_query(self, title, year):
        result = self.__make_query(
            method="VideoLibrary.GetMovies",
            params={
                "properties": ["uniqueid", "title", "originaltitle", "file"],
                "filter": {
                    "and": [
                        {"field": "title", "operator": "startswith", "value": title},
                        {
                            "or": [
                                {
                                    "field": "year",
                                    "operator": "is",
                                    "value": str(year - 1),
                                },
                                {"field": "year", "operator": "is", "value": str(year)},
                                {
                                    "field": "year",
                                    "operator": "is",
                                    "value": str(year + 1),
                                },
                            ]
                        },
                    ]
                },
            },
        )

        return result.get("movies", {})

    def _process_movie_item(self, db_item, all_info):
        source = None
        if db_item.get("file", "").endswith(".strm"):
            return None

        db_details = self.__make_query(
            method="VideoLibrary.GetMovieDetails",
            params={
                "properties": ["streamdetails", "file", "uniqueid"],
                "movieid": db_item.get("movieid", ""),
            },
        ).get("moviedetails", {})
        external_ids = db_details.get("uniqueid", {})
        movie_ids = {
            "tmdb": all_info['info'].get("tmdb_id"),
            "imdb": all_info['info'].get("imdb_id"),
            "trakt": all_info['info'].get("trakt_id"),
        }

        if all([external_ids.get(i) in [None, movie_ids[i]] for i in movie_ids]):
            source_info = get_file_info(db_details)
            source = {
                "scraper": self._scraper,
                "release_title": db_details['label'],
                "info": source_info['info'],
                "size": source_info['size'],
                "quality": source_info['quality'],
                "url": db_details.get('file', ''),
            }

        return source

    # def episode(self, simple_info, all_info):
    #     self.start_time = time.time()
    #     sources = []

    #     show_title = simple_info["show_title"]

    #     try:
    #         self._api = JustWatch(country=self._country)
    #         items = self._make_show_query(show_title)

    #         for item in items:
    #             source = self._process_show_item(item, simple_info, all_info)
    #             if source is not None:
    #                 sources.append(source)
    #                 break
    #     except PreemptiveCancellation:
    #         return self._return_results("episode", sources, preemptive=True)

    #     return self._return_results("episode", sources)

    def movie(self, simple_info, all_info):
        self.start_time = time.time()
        sources = []
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
                    sources.append(source)
                    break
        except PreemptiveCancellation:
            return self._return_results("movie", sources, preemptive=True)

        return self._return_results("movie", sources)
