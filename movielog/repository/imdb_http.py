from dataclasses import dataclass, field
from typing import Literal, get_args

import imdb

from movielog.repository.imdb_http_release_date import get_release_date

imdb_http = imdb.Cinemagoer(reraiseExceptions=True)


CreditKind = Literal["director", "writer", "performer"]

CREDIT_KINDS = get_args(CreditKind)

IMDbDataAccessError = imdb.IMDbDataAccessError


@dataclass
class TitleCredit:
    kind: CreditKind
    imdb_id: str
    full_title: str


@dataclass
class NamePage:
    credits: dict[CreditKind, list[TitleCredit]]


@dataclass
class NameCredit:
    kind: CreditKind
    sequence: int
    imdb_id: str
    name: str
    notes: str | None = None
    roles: list[str] = field(default_factory=list)


@dataclass
class TitlePage:
    imdb_id: str
    production_status: str | None
    kind: str
    credits: dict[CreditKind, list[NameCredit]]
    full_title: str
    genres: list[str]
    countries: list[str]
    sound_mix: set[str]
    release_date: str


def _parse_roles(person: imdb.Person.Person) -> list[str]:
    if isinstance(person.currentRole, list):
        return [role["name"] for role in person.currentRole if role.keys()]

    if person.currentRole.has_key("name"):
        return [person.currentRole["name"]]

    return []


def _build_title_credits_for_name_page(
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
                imdb_id=f"tt{credit.movieID}",
                full_title=credit["long imdb title"],
            )
            for credit in imdb_name_page["filmography"].get(kind, [])
        ]

    return credits


def _build_name_credits_for_title_page(  # noqa: WPS210, WPS231
    imdb_title_page: imdb.Movie.Movie,
) -> dict[CreditKind, list[NameCredit]]:
    credit_kind_map: dict[CreditKind, str] = {
        "director": "directors",
        "performer": "cast",
        "writer": "writers",
    }

    credits: dict[CreditKind, list[NameCredit]] = {}

    for credit_kind, imdb_key in credit_kind_map.items():
        credits[credit_kind] = []

        for index, imdb_credit in enumerate(imdb_title_page.get(imdb_key, [])):
            if "name" not in imdb_credit.keys():
                continue

            name_credit = NameCredit(
                sequence=index,
                kind=credit_kind,
                imdb_id=f"nm{imdb_credit.personID}",
                name=imdb_credit["name"],
                notes=imdb_credit.notes if imdb_credit.notes else None,
            )

            if credit_kind == "performer":
                name_credit.roles = _parse_roles(imdb_credit)

            credits[credit_kind].append(name_credit)

    return credits


def get_name_page(imdb_id: str) -> NamePage:
    imdb_name_page = imdb_http.get_person(imdb_id[2:])

    return NamePage(credits=_build_title_credits_for_name_page(imdb_name_page))


def get_title_page(imdb_id: str) -> TitlePage:
    imdb_movie = imdb_http.get_movie(imdb_id[2:], info=("main"))

    return TitlePage(
        imdb_id=f"tt{imdb_movie.movieID}",
        production_status=imdb_movie.get("production status", None),
        kind=imdb_movie.get("kind", "Unknown"),
        full_title=imdb_movie["long imdb title"],
        genres=imdb_movie.get("genres", []),
        countries=imdb_movie.get("countries", []),
        sound_mix=set(imdb_movie.get("sound mix", [])),
        credits=_build_name_credits_for_title_page(imdb_movie),
        release_date=get_release_date(imdb_id, imdb_movie.get("year")),
    )
