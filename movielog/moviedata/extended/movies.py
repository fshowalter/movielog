from dataclasses import dataclass
from datetime import date
from typing import Optional

import imdb

from movielog.moviedata.extended import (
    cast,
    directors,
    release_dates,
    serializer,
    writers,
)
from movielog.moviedata.extended.tables import api as tables_api

imdb_http = imdb.IMDb(reraiseExceptions=True)


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

    serializer.serialize(movie)

    return movie


def update(imdb_ids: set[str]) -> None:
    all_movie_data = serializer.deserialize_all()
    existing_imdb_ids = set(movie_data.imdb_id for movie_data in all_movie_data)

    for imdb_id in imdb_ids - existing_imdb_ids:
        new_movie = fetch(imdb_id)
        serializer.serialize(new_movie)
        all_movie_data.append(new_movie)

    tables_api.update_directing_credits(all_movie_data)
    tables_api.update_performing_credits(all_movie_data)
    tables_api.update_writing_credits(all_movie_data)
    tables_api.update_release_dates(all_movie_data)
    tables_api.update_countries(all_movie_data)
    tables_api.update_sort_titles(all_movie_data)
