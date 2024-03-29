# -*- coding: utf-8 -*-
from resources.lib.common.source_utils import de_string_size

from providerModules.a4kOfficial import common
from providerModules.a4kOfficial.core import Core


class LibraryCore(Core):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_quality(width):
        if width == 0:
            return "Unknown"
        elif width >= 2160:
            return "4K"
        elif width >= 1920:
            return "1080p"
        elif width >= 1280:
            return "720p"
        elif width < 1280:
            return "SD"

    @staticmethod
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
        file_info["size"] = de_string_size(common.convert_size(size))

        stream_details = db_details.get("streamdetails", {})
        audio_details = stream_details.get("audio", [])
        audio_details = audio_details[0] if len(audio_details) > 0 else {}
        video_details = stream_details.get("video", [])
        video_details = video_details[0] if len(video_details) > 0 else {}

        file_info["info"] = set()
        if audio_channels := audio_details.get("channels"):
            file_info["info"].add(f"{audio_channels}ch")
        if audio_codec := audio_details.get("codec"):
            file_info["info"].add("dts" if audio_codec == "dca" else audio_codec)
        if video_codec := video_details.get("codec"):
            file_info["info"].add("h264" if video_codec == "avc1" else video_codec)
        if video_codec := video_details.get("stereomode"):
            file_info["info"].add("3D")

        file_info["quality"] = LibraryCore.get_quality(video_details.get("width", 0))

        return file_info

    def _make_source(self, item, ids, source_info, db_details, **kwargs):
        source = super()._make_source(item, ids, source_info, db_details, **kwargs)
        source.update(
            {
                "release_title": db_details["label"],
                "info": source_info["info"],
                "size": source_info["size"],
                "quality": source_info["quality"],
                "url": db_details.get("file", ""),
            }
        )

        return source

    def __make_query(self, method, params, **kwargs):
        result = common.execute_jsonrpc(method=method, params=params, **kwargs).get("result", {})

        return result

    def _make_show_query(self, **kwargs):
        result = self.__make_query(
            method="VideoLibrary.GetTVShows",
            params={
                "properties": ["uniqueid", "title"],
            },
        )

        return result.get("tvshows", {})

    def _make_movie_query(self, **kwargs):
        result = self.__make_query(
            method="VideoLibrary.GetMovies",
            params={
                "properties": ["uniqueid", "title", "originaltitle", "file"],
                "filter": {
                    "and": [
                        {"field": "title", "operator": "startswith", "value": kwargs['title']},
                        {
                            "or": [
                                {
                                    "field": "year",
                                    "operator": "is",
                                    "value": str(kwargs['year'] - 1),
                                },
                                {"field": "year", "operator": "is", "value": str(kwargs['year'])},
                                {
                                    "field": "year",
                                    "operator": "is",
                                    "value": str(kwargs['year'] + 1),
                                },
                            ]
                        },
                    ]
                },
            },
        )

        return result.get("movies", {})

    def _process_item(self, db_item, simple_info, info, type, **kwargs):
        source = None
        db_details = None
        external_ids = None
        ids = None

        if type == "movie":
            db_details = self.__make_query(
                method="VideoLibrary.GetMovieDetails",
                params={
                    "properties": ["streamdetails", "file", "uniqueid"],
                    "movieid": db_item.get("movieid", ""),
                },
            ).get("moviedetails", {})
            if not db_details:
                return None

            external_ids = db_details.get("uniqueid", {})
            ids = {
                "tmdb": info["info"].get("tmdb_id"),
                "imdb": info["info"].get("imdb_id"),
                "trakt": info["info"].get("trakt_id"),
            }
        elif type == "episode":
            db_details = self.__make_query(
                method="VideoLibrary.GetEpisodes",
                params={
                    "properties": ["streamdetails", "file", "uniqueid"],
                    "tvshowid": db_item.get("tvshowid", ""),
                    "filter": {
                        "and": [
                            {
                                "field": "season",
                                "operator": "is",
                                "value": str(info["info"]["season"]),
                            },
                            {
                                "field": "episode",
                                "operator": "is",
                                "value": str(info["info"]["episode"]),
                            },
                        ]
                    },
                },
            )

            db_details = db_details.get("episodes", [])
            if not db_details:
                return None

            db_details = db_details[0]
            external_ids = db_item.get("uniqueid", {})
            ids = {
                "tmdb": info["info"].get("tmdb_show_id"),
                "tvdb": info["info"].get("tvdb_show_id"),
                "trakt": info["info"].get("trakt_show_id"),
            }

        if all(
            [int(external_ids.get(i, -1)) if not i == "imdb" else external_ids.get(i, -1) in [-1, ids[i]] for i in ids]
        ):
            source_info = self.get_file_info(db_details)
            source = self._make_source(None, ids, source_info, db_details)

        return source
