from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from typing import Sequence, cast

from movielog.utils.logging import logger
from movielog.watchlist import filmography, movies, person, serializer


@dataclass
class Writer(person.Person):
    folder_name = "writers"


def deserialize(file_path: str) -> Writer:
    json_person = None

    with open(file_path, "r") as json_file:
        json_person = cast(person.JsonPerson, json.load(json_file))

    return Writer(
        imdb_id=json_person["imdb_id"],
        frozen=json_person["frozen"],
        slug=json_person["slug"],
        name=json_person["name"],
        titles=movies.deserialize(json_person["movies"]),
    )


def deserialize_all() -> Sequence[Writer]:
    return serializer.deserialize_all(Writer.folder_name, deserialize)


def movies_for_writer(person_imdb_id: str, name: str) -> list[movies.Movie]:
    logger.log(
        "==== Begin getting {} credits for {}...",
        "writing",
        name,
    )

    return filmography.for_writer(person_imdb_id)


def refresh_movies() -> None:
    writers = deserialize_all()
    for writer in writers:
        if writer.frozen:
            continue
        writer_copy = copy.deepcopy(writer)
        writer_copy.titles = movies_for_writer(writer_copy.imdb_id, writer_copy.name)

        serializer.serialize(writer_copy)


def add(imdb_id: str, name: str) -> Writer:
    writer = Writer(
        frozen=False,
        name=name,
        imdb_id=imdb_id,
        slug=person.slug_for_name(name),
        titles=movies_for_writer(imdb_id, name),
    )
    serializer.serialize(writer)

    return writer
