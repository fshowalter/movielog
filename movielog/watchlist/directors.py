import copy
import json
from dataclasses import dataclass
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

    return Director(
        imdb_id=json_person["imdb_id"],
        frozen=json_person["frozen"],
        slug=json_person["slug"],
        name=json_person["name"],
        movies=movies.deserialize(json_person["movies"]),
    )


def deserialize_all() -> Sequence[Director]:
    return serializer.deserialize_all(Director.folder_name, deserialize)


def movies_for_director(person_imdb_id: str, name: str) -> list[movies.Movie]:
    logger.log(
        "==== Begin getting {} credits for {}...",
        "director",
        name,
    )

    return filmography.for_director(person_imdb_id)


def refresh_movies() -> None:
    directors = deserialize_all()
    for director in directors:
        if director.frozen:
            continue
        director_copy = copy.deepcopy(director)
        director_copy.movies = movies_for_director(
            director_copy.imdb_id, director_copy.name
        )

        serializer.serialize(director_copy)


def add(imdb_id: str, name: str) -> Director:
    director = Director(
        frozen=False,
        name=name,
        imdb_id=imdb_id,
        slug=person.slug_for_name(name),
        movies=movies_for_director(imdb_id, name),
    )
    serializer.serialize(director)

    return director
