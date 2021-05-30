from __future__ import annotations

import json
import os
from dataclasses import asdict
from glob import glob
from typing import TYPE_CHECKING, Any

from slugify import slugify

from movielog.moviedata.extended import cast, directors, writers
from movielog.utils import format_tools, path_tools
from movielog.utils.logging import logger

if TYPE_CHECKING:
    from movielog.moviedata.extended.movies import Movie


FOLDER_NAME = "data"


def deserialize_json_movie(json_movie: dict[str, Any]) -> Movie:
    return Movie(
        imdb_id=json_movie["imdb_id"],
        sort_title=json_movie["sort_title"],
        cast=cast.deserialize(json_movie["cast"]),
        directors=directors.deserialize(json_movie["directors"]),
        writers=writers.deserialize(json_movie["writers"]),
        countries=json_movie["countries"],
        release_date=json_movie["release_date"],
        release_date_notes=json_movie["release_date_notes"],
    )


def deserialize_all() -> list[Movie]:
    logger.log("==== Begin deserializing {}...", "movie data files")
    movies: list[Movie] = []

    for file_path in glob(os.path.join(FOLDER_NAME, "*.json")):
        with open(file_path, "r") as json_file:
            movies.append(deserialize_json_movie(json.load(json_file)))

    logger.log(
        "Deserialized {} files.",
        format_tools.humanize_int(len(movies)),
    )

    return movies


def serialize(movie: Movie) -> None:
    file_path = os.path.join(FOLDER_NAME, "{0}.json".format(slugify(movie.sort_title)))
    path_tools.ensure_file_path(file_path)

    with open(file_path, "w") as output_file:
        output_file.write(json.dumps(asdict(movie), default=str, indent=2))

    logger.log(
        "Wrote {} with {} directors, {} writers, and {} performers.",
        file_path,
        format_tools.humanize_int(len(movie.directors)),
        format_tools.humanize_int(len(movie.writers)),
        format_tools.humanize_int(len(movie.cast)),
    )
