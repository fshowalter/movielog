from dataclasses import dataclass
from typing import Literal, Optional, get_args

import imdb

imdb_http = imdb.Cinemagoer(reraiseExceptions=True)


CreditKind = Literal["director", "writer", "performer"]

CREDIT_KINDS = get_args(CreditKind)


@dataclass
class TitleCredit(object):
    kind: CreditKind
    imdb_id: str
    full_title: str


@dataclass
class NamePage(object):
    credits: dict[CreditKind, list[TitleCredit]]


@dataclass
class NameCredit(object):
    kind: CreditKind
    imdb_id: str
    name: str
    notes: Optional[str] = None


@dataclass
class TitlePage(object):
    imdb_id: str
    production_status: Optional[str]
    kind: str
    credits: dict[CreditKind, list[NameCredit]]
    full_title: str
    genres: set[str]
    sound_mix: set[str]

    def credits_for_person(
        self, person_imdb_id: str, kind: CreditKind
    ) -> list[NameCredit]:
        return [
            credit for credit in self.credits[kind] if credit.imdb_id == person_imdb_id
        ]

    def invalid_credits_for_person(
        self, person_imdb_id: str, kind: CreditKind
    ) -> list[NameCredit]:
        return [
            credit
            for credit in self.credits_for_person(person_imdb_id, kind)
            if credit.notes
            and ("scenes deleted" in credit.notes or "uncredited" in credit.notes)
        ]


def build_title_credits_for_name_page(
    imdb_name_page: imdb.Person.Person,
) -> dict[CreditKind, list[TitleCredit]]:
    credits = {}

    filmography = imdb_name_page["filmography"]

    filmography["performer"] = filmography.pop(
        "actor",
        [],
    ) + filmography.pop(
        "actress",
        [],
    )

    for kind in CREDIT_KINDS:
        credits[kind] = [
            TitleCredit(
                kind=kind,
                imdb_id="tt{0}".format(credit.movieID),
                full_title=credit["long imdb title"],
            )
            for credit in imdb_name_page["filmography"][kind]
        ]

    return credits


def build_name_credits_for_title_page(
    imdb_title_page: imdb.Movie.Movie,
) -> dict[CreditKind, list[NameCredit]]:
    credit_kind_map: dict[CreditKind, str] = {
        "director": "directors",
        "performer": "cast",
        "writer": "writers",
    }

    credits = {}

    for credit_kind, imdb_key in credit_kind_map.items():
        credits[credit_kind] = [
            NameCredit(
                kind=credit_kind,
                imdb_id="nm{0}".format(credit.personID),
                name=credit["name"],
                notes=credit.notes if credit.notes else None,
            )
            for credit in imdb_title_page[imdb_key]
        ]

    return credits


def get_name_page(imdb_id: str) -> NamePage:
    imdb_name_page = imdb_http.get_person(imdb_id[2:])

    return NamePage(credits=build_title_credits_for_name_page(imdb_name_page))


def get_title_page(imdb_id: str) -> TitlePage:
    imdb_movie = imdb_http.get_movie(imdb_id[2:])

    return TitlePage(
        imdb_id="tt{0}".format(imdb_movie.movieID),
        production_status=imdb_movie.get("production status", None),
        kind=imdb_movie["kind"],
        full_title=imdb_movie["long imdb title"],
        genres=set(imdb_movie.get("genres", [])),
        sound_mix=set(imdb_movie.get("sound mix", [])),
        credits=build_name_credits_for_title_page(imdb_movie),
    )
