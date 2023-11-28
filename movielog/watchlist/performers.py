from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from typing import Sequence, cast

from movielog.utils.logging import logger
from movielog.watchlist import filmography, movies, person, serializer


@dataclass
class Performer(person.Person):
    folder_name = "performers"


def deserialize(file_path: str) -> Director:
    json_person = None

    with open(file_path, "r") as json_file:
        json_person = cast(person.JsonPerson, json.load(json_file))

    json_titles = []

    if "titles" in json_person.keys():
        json_titles = json_person["titles"]

    excluded_titles = []

    imdb_id = json_person["imdbIds"]

    if len(imdb_id) == 1:
        imdb_id = imdb_id[0]

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

    return Performer(
        imdbId=json_person["imdb_id"],
        slug=json_person["slug"],
        name=json_person["name"],
        titles=json_titles,
        excludedTitles=excluded_titles,
    )


def deserialize_all() -> Sequence[Performer]:
    return serializer.deserialize_all(Performer.folder_name, deserialize)


def movies_for_performer(person_imdb_id: str, name: str) -> list[movies.Movie]:
    logger.log(
        "==== Begin getting {} credits for {}...",
        "performer",
        name,
    )

    return filmography.for_performer(person_imdb_id)


def refresh_movies() -> None:
    performers = deserialize_all()
    for performer in performers:
        # if director.frozen:
        #     continue
        logger.log(
            "==== Begin getting {} credits for {}...",
            "performer",
            performer.name,
        )

        performer = filmography.for_performer(performer)

        serializer.serialize(performer, performer.folder_name)


def add(imdb_id: str, name: str) -> Performer:
    performer = Performer(
        frozen=False,
        name=name,
        imdb_id=imdb_id,
        slug=person.slug_for_name(name),
        titles=movies_for_performer(imdb_id, name),
    )
    serializer.serialize(performer)

    return performer
