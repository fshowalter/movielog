from __future__ import annotations

import copy
import json
from dataclasses import asdict, dataclass
from typing import Sequence, cast

from movielog.utils.logging import logger
from movielog.watchlist import filmography, movies, person, serializer


@dataclass
class Director(person.Person):
    folder_name = "directors"


def deserialize(file_path: str) -> Director:
    json_person = None

    with open(file_path, "r") as json_file:
        json_person = cast(person.JsonPerson, json.load(json_file))

    json_titles = []

    if "titles" in json_person.keys():
        json_titles = json_person["titles"]
    else:
        json_titles = json_person["movies"]

    excluded_titles = []

    # imdb_id = json_person["imdbIds"]

    # if len(imdb_id) == 1:
    #     imdb_id = imdb_id[0]

    # if "imdb_id" in json_person.keys():
    #     imdb_ids = [json_person["imdb_id"]]
    # elif "imdbId" in json_person.keys():
    #     imdb_ids = [json_person["imdbId"]]
    # else:
    #     imdb_ids = json_person["imdbIds"]

    if "excludedTitles" in json_person.keys():
        excluded_titles = [
            movies.JsonExcludedTitle(
                imdbId=json_excluded_title["imdbId"],
                title=json_excluded_title["title"],
                reason=json_excluded_title["reason"],
            )
            for json_excluded_title in json_person["excludedTitles"]
        ]

    return Director(
        imdbId=json_person["imdbId"],
        slug=json_person["slug"],
        name=json_person["name"],
        titles=json_titles,
        excludedTitles=excluded_titles,
    )


def deserialize_all() -> Sequence[Director]:
    return serializer.deserialize_all(Director.folder_name, deserialize)


def movies_for_director(
    director: Director, name: str, excludedTItles: list[movies.ExcludedTitle]
) -> list[movies.Movie]:
    logger.log(
        "==== Begin getting {} credits for {}...",
        "director",
        name,
    )

    return filmography.for_director(person_imdb_id, excludedTItles)


def refresh_movies() -> None:
    directors = deserialize_all()
    for director in directors:
        # if director.frozen:
        #     continue
        logger.log(
            "==== Begin getting {} credits for {}...",
            "director",
            director.name,
        )

        director = filmography.for_director(director)

        serializer.serialize(director, director.folder_name)


def add(imdb_id: str, name: str) -> Director:
    director = Director(
        frozen=False,
        name=name,
        imdb_id=imdb_id,
        slug=person.slug_for_name(name),
        titles=movies_for_director(imdb_id, name),
    )
    serializer.serialize(director)

    return director
