from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import date, datetime
from glob import glob
from typing import Any, Optional

import imdb
from slugify import slugify

from movielog.moviedata.extended import cast, directors, release_dates, writers
from movielog.moviedata.extended.tables import api as tables_api
from movielog.utils import format_tools, path_tools
from movielog.utils.logging import logger

imdb_http = imdb.IMDb(reraiseExceptions=True)

FOLDER_NAME = "data"


@dataclass
class Movie(object):
    imdb_id: str
    sort_title: str
    directors: list[directors.Credit]
    cast: list[cast.Credit]
    writers: list[writers.Credit]
    release_date: date
    release_date_notes: Optional[str]
    countries: list[str]


def generate_sort_title(title: str, year: str) -> str:
    title_with_year = "{0} ({1})".format(title, year)
    title_lower = title_with_year.lower()
    title_words = title_with_year.split(" ")
    lower_words = title_lower.split(" ")
    articles = set(["a", "an", "the"])

    if (len(title_words) > 1) and (lower_words[0] in articles):
        return "{0}".format(" ".join(title_words[1 : len(title_words)]))

    return title_with_year


def fetch(
    title_imdb_id: str,
) -> Movie:
    imdb_movie = imdb_http.get_movie(title_imdb_id[2:], info=["main", "release_dates"])

    release_date = release_dates.parse(imdb_movie)

    movie = Movie(
        imdb_id=title_imdb_id,
        sort_title=generate_sort_title(
            title=imdb_movie["title"], year=imdb_movie["year"]
        ),
        release_date=release_date.date,
        release_date_notes=release_date.notes,
        directors=directors.parse(imdb_movie),
        writers=writers.parse(imdb_movie),
        cast=cast.parse(imdb_movie),
        countries=imdb_movie["countries"],
    )

    serialize(movie)

    return movie


def deserialize_json_movie(json_movie: dict[str, Any]) -> Movie:
    return Movie(
        imdb_id=json_movie["imdb_id"],
        sort_title=json_movie["sort_title"],
        cast=cast.deserialize(json_movie["cast"]),
        directors=directors.deserialize(json_movie["directors"]),
        writers=writers.deserialize(json_movie["writers"]),
        countries=json_movie["countries"],
        release_date=datetime.fromisoformat(json_movie["release_date"]).date(),
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
    slug = slugify(movie.sort_title, replacements=[("'", "")])
    file_path = os.path.join(FOLDER_NAME, "{0}.json".format(slug))
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


def update(imdb_ids: set[str]) -> None:
    all_movie_data = deserialize_all()
    existing_imdb_ids = set(movie_data.imdb_id for movie_data in all_movie_data)

    for imdb_id in imdb_ids - existing_imdb_ids:
        new_movie = fetch(imdb_id)
        all_movie_data.append(new_movie)

    tables_api.reload(all_movie_data)
