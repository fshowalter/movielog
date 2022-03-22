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


def deserialize(file_path: str) -> Performer:
    json_person = None

    with open(file_path, "r") as json_file:
        json_person = cast(person.JsonPerson, json.load(json_file))

    return Performer(
        imdb_id=json_person["imdb_id"],
        frozen=json_person["frozen"],
        slug=json_person["slug"],
        name=json_person["name"],
        movies=movies.deserialize(json_person["movies"]),
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
        if performer.frozen:
            continue
        performer_copy = copy.deepcopy(performer)
        performer_copy.movies = movies_for_performer(
            performer_copy.imdb_id, performer_copy.name
        )

        serializer.serialize(performer_copy)


def add(imdb_id: str, name: str) -> Performer:
    performer = Performer(
        frozen=False,
        name=name,
        imdb_id=imdb_id,
        slug=person.slug_for_name(name),
        movies=movies_for_performer(imdb_id, name),
    )
    serializer.serialize(performer)

    return performer
