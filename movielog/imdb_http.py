import fnmatch
from collections import ChainMap
from dataclasses import dataclass
from typing import Optional, Sequence, Set, List, Union

import imdb

silent_ids: Set[str] = set()
no_sound_mix_ids: Set[str] = set()
imdb_scraper = imdb.IMDb(reraiseExceptions=True)


@dataclass
class Movie(object):  # noqa: WPS230
    year: str
    title: str
    imdb_id: str
    movie_object: imdb.Movie.Movie
    notes: str
    cast_credits: Sequence["CastCredit"]

    @classmethod
    def from_imdb_id(cls, imdb_id: str) -> "Movie":
        imdb_movie = imdb_scraper.get_movie(imdb_id[2:])

        cast_credits = []

        for index, performer in enumerate(imdb_movie["cast"]):
            cast_credits.append(
                CastCredit.from_imdb_cast_credit(imdb_id, index, performer)
            )

        return Movie(
            year=imdb_movie.get("year", "????"),
            title=imdb_movie["title"],
            imdb_id=imdb_id,
            movie_object=imdb_movie,
            notes=imdb_movie.notes,
            cast_credits=cast_credits,
        )


@dataclass
class CastCredit(object):
    movie_imdb_id: str
    person_imdb_id: str
    name: str
    roles: List[str]
    notes: Optional[str]
    sequence: int

    @classmethod
    def from_imdb_cast_credit(
        cls, imdb_id: str, sequence: int, performer: imdb.Person.Person
    ) -> "CastCredit":
        return cls(
            movie_imdb_id=imdb_id,
            sequence=sequence,
            person_imdb_id=f"tt{performer.personID}",
            name=performer["name"],
            roles=cls.parse_role(performer.currentRole),
            notes=performer.notes,
        )

    @classmethod
    def parse_role(
        cls, roles: Union[imdb.Character.Character, imdb.utils.RolesList]
    ) -> List[str]:
        if isinstance(roles, imdb.Character.Character):
            name = roles.get("name")
            if name:
                return [name]

            return []

        return [role["name"] for role in roles]


@dataclass
class MovieOld(object):  # noqa: WPS230
    year: str
    title: str
    imdb_id: str
    movie_object: imdb.Movie.Movie
    notes: str
    in_production: bool = False
    is_silent: Optional[bool] = None
    has_sound_mix: Optional[bool] = None
    cast: Optional[Sequence["CastCredit"]] = None

    @classmethod
    def from_imdb_movie(cls, imdb_movie: imdb.Movie.Movie) -> "MovieOld":
        movie = MovieOld(
            year=imdb_movie.get("year", "????"),
            title=imdb_movie["title"],
            imdb_id=f"tt{imdb_movie.movieID}",
            movie_object=imdb_movie,
            notes=imdb_movie.notes,
        )

        in_production = imdb_movie.get("status")
        if in_production:
            movie.in_production = True
            movie.notes = f"({in_production})"

        if movie.imdb_id in no_sound_mix_ids:
            movie.has_sound_mix = False
        elif movie.imdb_id in silent_ids:
            movie.has_sound_mix = True
            movie.is_silent = True
        else:
            imdb_scraper.update(movie.movie_object, info=["technical"])
            if movie_has_sound_mix(movie):
                movie.has_sound_mix = True
                movie.is_silent = movie_is_silent(movie)
            else:
                movie.has_sound_mix = False
                movie.is_silent = None

        movie.cast = []
        for index, performer in enumerate(imdb_movie["cast"]):
            movie.cast.append(
                CastCredit(
                    movie_imdb_id=movie.imdb_id,
                    person_imdb_id=f"tt{performer.personIDp}",
                    name=performer["name"],
                    role=performer.currentRole,
                    notes=performer.notes,
                    sequence=index,
                )
            )

        return movie


class Person(object):
    def __init__(self, imdb_id: str) -> None:
        self.imdb_id = imdb_id
        imdb_person = imdb_scraper.get_person(imdb_id[2:])
        self.name = imdb_person["name"]
        self.filmography = dict(ChainMap(*imdb_person["filmography"]))
        self.filmography["performer"] = self.filmography.get(
            "actor", [],
        ) + self.filmography.get("actress", [],)


def get_movie(imdb_id: str) -> "Movie":
    return Movie.from_imdb_id(imdb_id)


def movie_has_sound_mix(movie: MovieOld) -> bool:
    if movie.imdb_id in no_sound_mix_ids:
        return False

    if "sound mix" in movie.movie_object["technical"]:
        return True

    no_sound_mix_ids.add(movie.imdb_id)

    return False


def movie_is_silent(movie: MovieOld) -> bool:
    if movie.imdb_id in silent_ids:
        return True

    pattern = "Silent*"

    sound_mixes = movie.movie_object["technical"]["sound mix"]
    if fnmatch.filter(sound_mixes, pattern):
        silent_ids.add(movie.imdb_id)
        return True

    return False
