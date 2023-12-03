from dataclasses import dataclass
from typing import Literal, Optional, get_args

import imdb

imdb_http = imdb.Cinemagoer(reraiseExceptions=True)

NameCreditKind = Literal[
    "directors",
    "writers",
    "performers",
]

NAME_CREDIT_KINDS = get_args(NameCreditKind)

TitleCreditKind = Literal["director", "writer", "performer"]

TITLE_CREDIT_KINDS = get_args(TitleCreditKind)


@dataclass
class TitleCredit(object):
    imdb_id: str
    full_title: str


@dataclass
class Person(object):
    credits: dict[TitleCreditKind, list[TitleCredit]]


@dataclass
class NameCredit(object):
    imdb_id: str
    name: str
    notes: Optional[str] = None


@dataclass
class Movie(object):
    imdb_id: str
    production_status: Optional[str]
    kind: str
    credits: dict[NameCreditKind, list[NameCredit]]
    full_title: str
    genres: set[str]
    sound_mix: set[str]

    def credits_for_person(
        self, person_imdb_id: str, kind: NameCreditKind
    ) -> list[NameCredit]:
        return [
            credit for credit in self.credits[kind] if credit.imdb_id == person_imdb_id
        ]

    def invalid_credits_for_person(
        self, person_imdb_id: str, kind: NameCreditKind
    ) -> list[NameCredit]:
        return [
            credit
            for credit in self.credits_for_person(person_imdb_id, kind)
            if credit.notes
            and ("scenes deleted" in credit.notes or "uncredited" in credit.notes)
        ]


def build_title_credits_for_person(
    imdb_person: imdb.Person.Person,
) -> dict[TitleCreditKind, list[TitleCredit]]:
    credits = {}

    filmography = imdb_person["filmography"]

    filmography["performer"] = filmography.pop(
        "actor",
        [],
    ) + filmography.pop(
        "actress",
        [],
    )

    for kind in TITLE_CREDIT_KINDS:
        credits[kind] = [
            TitleCredit(
                imdb_id="tt{0}".format(credit.movieID),
                full_title=credit["long imdb title"],
            )
            for credit in imdb_person["filmography"][kind]
        ]

    return credits


def build_name_credits_for_movie(
    imdb_movie: imdb.Movie.Movie,
) -> dict[NameCreditKind, list[NameCredit]]:
    name_credit_kind_map: dict[NameCreditKind, str] = {
        "directors": "director",
        "performers": "cast",
        "writers": "writers",
    }

    credits = {}

    for name_credit_kind, imdb_key in name_credit_kind_map.items():
        credits[name_credit_kind] = [
            NameCredit(
                imdb_id="nm{0}".format(credit.personID),
                name=credit["name"],
                notes=credit.notes if credit.notes else None,
            )
            for credit in imdb_movie[imdb_key]
        ]

    return credits


def get_person(imdb_id: str) -> Person:
    imdb_person = imdb_http.get_person(imdb_id[2:])

    return Person(credits=build_title_credits_for_person(imdb_person))


def get_movie(imdb_id: str) -> Movie:
    imdb_movie = imdb_http.get_movie(imdb_id[2:])

    return Movie(
        imdb_id="tt{0}".format(imdb_movie.movieID),
        production_status=imdb_movie.get("production status", None),
        kind=imdb_movie["kind"],
        full_title=imdb_movie["long imdb title"],
        genres=set(imdb_movie.get("genres", [])),
        sound_mix=set(imdb_movie.get("sound mix", [])),
        credits=build_name_credits_for_movie(imdb_movie),
    )
