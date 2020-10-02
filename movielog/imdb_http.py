import fnmatch
import time
from collections import ChainMap
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List, Optional, Sequence, Set, Tuple, Union

import imdb

silent_ids: Set[str] = set()
no_sound_mix_ids: Set[str] = set()
imdb_scraper = imdb.IMDb(reraiseExceptions=True)

TITLE = "title"
YEAR = "year"
EMPTY_STRING = ""


@dataclass
class TitleBasic(object):
    imdb_id: str
    title: str
    year: int


@dataclass
class CreditForPerson(TitleBasic):
    notes: str
    in_production: Optional[str]

    @classmethod
    def from_imdb_movie(cls, imdb_movie: imdb.Movie.Movie) -> "CreditForPerson":
        return cls(
            imdb_id=f"tt{imdb_movie.movieID}",
            year=imdb_movie.get(YEAR, "????"),
            title=imdb_movie[TITLE],
            notes=imdb_movie.notes,
            in_production=imdb_movie.get("status"),
        )


@dataclass
class CastCreditForTitle(object):
    movie_imdb_id: str
    person_imdb_id: str
    name: str
    roles: List[str]
    notes: Optional[str]
    sequence: int

    @classmethod
    def from_imdb_cast_credit(
        cls, imdb_id: str, sequence: int, cast_credit: imdb.Person.Person
    ) -> "CastCreditForTitle":
        return cls(
            movie_imdb_id=imdb_id,
            sequence=sequence,
            person_imdb_id=f"nm{cast_credit.personID}",
            name=cast_credit["name"],
            roles=cls.parse_role(cast_credit.currentRole),
            notes=cast_credit.notes,
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
class TitleDetail(TitleBasic):
    countries: List[str]


def countries_for_title(
    title_imdb_id: str,
) -> TitleDetail:
    imdb_movie = imdb_scraper.get_movie(title_imdb_id[2:])

    return TitleDetail(
        imdb_id=title_imdb_id,
        year=imdb_movie.get(YEAR, "????"),
        title=imdb_movie[TITLE],
        countries=imdb_movie.get("countries", []),
    )


@dataclass
class TitleReleaseDate(TitleBasic):
    release_date: date
    notes: Optional[str]

    @classmethod
    def parse_json_date(cls, json_date: str) -> date:
        try:
            return datetime.strptime(json_date, "%d %B %Y").date()  # noqa: WPS323
        except ValueError:
            try:  # noqa: WPS505
                return datetime.strptime(json_date, "%B %Y").date()
            except ValueError:
                return datetime.strptime(json_date, "%Y").date()

    @classmethod
    def is_just_a_year_from_romania(cls, json: Dict[str, str]) -> bool:
        return (
            json.get("country", EMPTY_STRING).strip() == "Romania"
            and len(json.get("date", EMPTY_STRING).strip()) == 4
        )


def release_date_for_title(
    title_imdb_id: str,
) -> TitleReleaseDate:
    imdb_movie = imdb_scraper.get_movie(
        title_imdb_id[2:], info=["main", "release_dates"]
    )

    raw_release_dates = imdb_movie.get("raw release dates")

    if not raw_release_dates:
        return TitleReleaseDate(
            imdb_id=title_imdb_id,
            title=imdb_movie[TITLE],
            year=imdb_movie[YEAR],
            release_date=date(imdb_movie.get(YEAR), 1, 1),
            notes=EMPTY_STRING,
        )

    release_dates: List[TitleReleaseDate] = []

    for release_date_json in raw_release_dates:
        if TitleReleaseDate.is_just_a_year_from_romania(release_date_json):
            continue

        release_dates.append(
            TitleReleaseDate(
                imdb_id=title_imdb_id,
                title=imdb_movie[TITLE],
                year=imdb_movie[YEAR],
                release_date=TitleReleaseDate.parse_json_date(
                    release_date_json.get("date", EMPTY_STRING).strip()
                ),
                notes=release_date_json.get("notes", EMPTY_STRING).strip(),
            )
        )

    most_recent = sorted(release_dates, key=lambda rd: rd.release_date)[0]

    if most_recent.release_date.year != int(imdb_movie.get(YEAR)):
        return TitleReleaseDate(
            imdb_id=title_imdb_id,
            title=imdb_movie[TITLE],
            year=imdb_movie[YEAR],
            release_date=date(imdb_movie.get(YEAR), 1, 1),
            notes="Given release date: {0} {1}".format(
                most_recent.release_date.isoformat(), most_recent.notes
            ),
        )

    return most_recent


def cast_credits_for_title(
    title_imdb_id: str,
) -> Tuple[TitleBasic, Sequence[CastCreditForTitle]]:
    imdb_movie = imdb_scraper.get_movie(title_imdb_id[2:])

    title_basic = TitleBasic(
        imdb_id=title_imdb_id, title=imdb_movie[TITLE], year=imdb_movie[YEAR]
    )

    cast_credit_list: List[CastCreditForTitle] = []

    for index, cast_credit in enumerate(imdb_movie["cast"]):
        cast_credit_list.append(
            CastCreditForTitle.from_imdb_cast_credit(
                imdb_id=title_imdb_id,
                sequence=index,
                cast_credit=cast_credit,
            )
        )

    return (title_basic, cast_credit_list)


def credits_for_person(
    person_imdb_id: str, credit_key: str
) -> Sequence[CreditForPerson]:
    imdb_person = imdb_scraper.get_person(person_imdb_id[2:])
    filmography = dict(ChainMap(*imdb_person["filmography"]))

    if credit_key == "performer":
        filmography["performer"] = filmography.pop("actor", [],) + filmography.pop(
            "actress",
            [],
        )

    credit_list: List[CreditForPerson] = []

    for imdb_movie in reversed(filmography.get(credit_key, [])):
        credit_list.append(CreditForPerson.from_imdb_movie(imdb_movie))

    return credit_list


def is_silent_film(title: TitleBasic) -> Optional[bool]:
    if title.imdb_id in silent_ids:
        return True

    if title.imdb_id in no_sound_mix_ids:
        return None

    time.sleep(1)
    imdb_movie = imdb.Movie.Movie(movieID=title.imdb_id[2:])
    imdb_scraper.update(imdb_movie, info=["technical"])

    if "sound mix" not in imdb_movie["technical"]:
        no_sound_mix_ids.add(title.imdb_id)
        return None

    pattern = "Silent*"

    sound_mixes = imdb_movie["technical"]["sound mix"]
    if fnmatch.filter(sound_mixes, pattern):
        silent_ids.add(title.imdb_id)
        return True

    return False
