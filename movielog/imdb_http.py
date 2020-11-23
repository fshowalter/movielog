import fnmatch
import re
import time
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional, Sequence, Set, Union

import imdb

silent_ids: Set[str] = set()
no_sound_mix_ids: Set[str] = set()
imdb_scraper = imdb.IMDb(reraiseExceptions=True)

TITLE = "title"
YEAR = "year"
EMPTY_STRING = ""
NAME = "name"
TT = "tt"


@dataclass
class TitleBasic(object):
    imdb_id: str
    title: str
    year: int

    def is_silent_film(self) -> Optional[bool]:
        if self.imdb_id in silent_ids:
            return True

        if self.imdb_id in no_sound_mix_ids:
            return None

        time.sleep(1)
        imdb_movie = imdb.Movie.Movie(movieID=self.imdb_id[2:])
        imdb_scraper.update(imdb_movie, info=["technical"])

        if "sound mix" not in imdb_movie["technical"]:
            no_sound_mix_ids.add(self.imdb_id)
            return None

        pattern = "Silent*"

        sound_mixes = imdb_movie["technical"]["sound mix"]
        if fnmatch.filter(sound_mixes, pattern):
            silent_ids.add(self.imdb_id)
            return True

        return False


@dataclass
class CreditForPerson(TitleBasic):
    notes: str
    in_production: Optional[str]

    @classmethod
    def from_imdb_movie(cls, imdb_movie: imdb.Movie.Movie) -> "CreditForPerson":
        return cls(
            imdb_id=f"{TT}{imdb_movie.movieID}",
            year=imdb_movie.get(YEAR, "????"),
            title=imdb_movie[TITLE],
            notes=imdb_movie.notes,
            in_production=imdb_movie.get("status"),
        )


@dataclass
class CreditForTitle(object):
    movie_imdb_id: str
    person_imdb_id: str
    sequence: int
    name: str
    notes: Optional[str]


@dataclass
class DirectingCreditForTitle(CreditForTitle):
    @classmethod
    def from_imdb_credit(
        cls, imdb_id: str, sequence: int, credit: imdb.Person.Person
    ) -> "DirectingCreditForTitle":
        return cls(
            movie_imdb_id=imdb_id,
            sequence=sequence,
            person_imdb_id=f"nm{credit.personID}",
            name=credit[NAME],
            notes=credit.notes,
        )


@dataclass
class WritingCreditForTitle(CreditForTitle):
    group: int

    invalid_notes = [
        "(based on characters created by)",
        "(character)",
        "(characters)",
        "(characters) (uncredited)",
        '("Alien" characters)',
        "(based on the Marvel comics by)",
        "(based on the Marvel comics by) and",
        "(based on characters created by)",
        "(based on elements created by)",
        "(excerpt)",
        "(comic book)",
        "(comic book) (uncredited)",
        "(Marvel comic book)",
        "(trading card series)",
        "(trading card series) (as Norm Saunders)",
    ]

    created_by_regex = re.compile(r"^\(.*created by\)( and)?$")
    character_created_by_regex = re.compile(r"\(character created by: (?:.*)\)$")

    @classmethod
    def credit_is_valid(cls, credit: imdb.Person.Person) -> bool:
        notes = credit.notes.strip()
        return (
            (notes not in cls.invalid_notes)
            and not cls.created_by_regex.match(notes)
            and not cls.character_created_by_regex.match(notes)
        )

    @classmethod
    def from_imdb_credit(
        cls, imdb_id: str, group: int, sequence: int, credit: imdb.Person.Person
    ) -> "WritingCreditForTitle":
        return cls(
            movie_imdb_id=imdb_id,
            group=group,
            sequence=sequence,
            person_imdb_id=f"nm{credit.personID}",
            name=credit[NAME],
            notes=credit.notes,
        )


@dataclass
class CastCreditForTitle(CreditForTitle):
    roles: List[str]

    invalid_notes = ["(uncredited)"]

    @classmethod
    def credit_is_valid(cls, credit: imdb.Person.Person) -> bool:
        notes = credit.notes.strip()
        return notes not in cls.invalid_notes

    @classmethod
    def from_imdb_cast_credit(
        cls, imdb_id: str, sequence: int, cast_credit: imdb.Person.Person
    ) -> "CastCreditForTitle":
        return cls(
            movie_imdb_id=imdb_id,
            sequence=sequence,
            person_imdb_id=f"nm{cast_credit.personID}",
            name=cast_credit[NAME],
            roles=cls.parse_role(cast_credit.currentRole),
            notes=cast_credit.notes,
        )

    @classmethod
    def parse_role(
        cls, roles: Union[imdb.Character.Character, imdb.utils.RolesList]
    ) -> List[str]:
        if isinstance(roles, imdb.Character.Character):
            name = roles.get(NAME)
            if name:
                return [name]

            return []

        return [role[NAME] for role in roles]


@dataclass
class ReleaseDate(object):
    date: date
    notes: Optional[str]


@dataclass
class TitleDetail(TitleBasic):
    release_date: date
    release_date_notes: Optional[str]

    directors: List[DirectingCreditForTitle]
    writers: List[WritingCreditForTitle]
    cast: List[CastCreditForTitle]

    @classmethod
    def parse_json_date(cls, json_date: str) -> Optional[date]:
        try:
            return datetime.strptime(json_date, "%d %B %Y").date()  # noqa: WPS323
        except ValueError:
            try:  # noqa: WPS505
                return datetime.strptime(json_date, "%B %Y").date()
            except ValueError:
                return None

    @classmethod
    def parse_directing_credits(
        cls, movie: imdb.Movie.Movie
    ) -> List[DirectingCreditForTitle]:
        credit_list: List[DirectingCreditForTitle] = []

        imdb_credits = movie.get("directors", [])

        for index, credit in enumerate(imdb_credits):
            credit_list.append(
                DirectingCreditForTitle.from_imdb_credit(
                    imdb_id=f"{TT}{movie['imdbID']}",
                    sequence=index,
                    credit=credit,
                )
            )

        return credit_list

    @classmethod
    def parse_writing_credits(
        cls, movie: imdb.Movie.Movie
    ) -> List[WritingCreditForTitle]:
        credit_list: List[WritingCreditForTitle] = []

        imdb_credits = movie.get("writers", [])
        credit_sequence = 0
        credit_group = 0

        for credit in imdb_credits:
            if not credit.keys():
                credit_group += 1
                credit_sequence = 0
                continue

            if not WritingCreditForTitle.credit_is_valid(credit):
                continue

            credit_list.append(
                WritingCreditForTitle.from_imdb_credit(
                    imdb_id=f"{TT}{movie['imdbID']}",
                    group=credit_group,
                    sequence=credit_sequence,
                    credit=credit,
                )
            )

        return credit_list

    @classmethod
    def parse_cast_credits(cls, movie: imdb.Movie.Movie) -> List[CastCreditForTitle]:
        credit_list: List[CastCreditForTitle] = []

        for index, filtered_credit in enumerate(movie.get("cast", [])):
            if not CastCreditForTitle.credit_is_valid(filtered_credit):
                continue

            credit_list.append(
                CastCreditForTitle.from_imdb_cast_credit(
                    imdb_id=f"{TT}{movie['imdbID']}",
                    sequence=index,
                    cast_credit=filtered_credit,
                )
            )

        return credit_list

    @classmethod
    def parse_release_date(cls, imdb_movie: imdb.Movie.Movie) -> Optional[ReleaseDate]:
        raw_release_dates = imdb_movie.get("raw release dates")

        if not raw_release_dates:
            return None

        release_dates: List[ReleaseDate] = []

        for release_date_json in raw_release_dates:
            release_date = cls.parse_json_date(
                release_date_json.get("date", EMPTY_STRING).strip()
            )

            if not release_date:
                continue

            release_dates.append(
                ReleaseDate(
                    date=release_date,
                    notes=release_date_json.get("notes", EMPTY_STRING).strip(),
                )
            )

        if not release_dates:
            return None

        most_recent = sorted(release_dates, key=lambda rd: rd.date)[0]

        if most_recent.date.year != int(imdb_movie.get(YEAR)):
            return ReleaseDate(
                date=date(imdb_movie.get(YEAR), 1, 1),
                notes="Given release date: {0} {1}".format(
                    most_recent.date.isoformat(), most_recent.notes
                ),
            )

        return most_recent

    @classmethod
    def from_imdb_id(cls, title_imdb_id: str) -> "TitleDetail":
        imdb_movie = imdb_scraper.get_movie(
            title_imdb_id[2:], info=["main", "release_dates"]
        )

        directors: List[DirectingCreditForTitle] = cls.parse_directing_credits(
            imdb_movie
        )
        writers: List[WritingCreditForTitle] = cls.parse_writing_credits(imdb_movie)
        cast: List[CastCreditForTitle] = cls.parse_cast_credits(imdb_movie)
        release_date = cls.parse_release_date(imdb_movie)

        if not release_date:
            return cls(
                imdb_id=title_imdb_id,
                title=imdb_movie[TITLE],
                year=imdb_movie[YEAR],
                release_date=date(imdb_movie.get(YEAR), 1, 1),
                release_date_notes="No release date",
                directors=directors,
                writers=writers,
                cast=cast,
            )

        return cls(
            imdb_id=title_imdb_id,
            title=imdb_movie[TITLE],
            year=imdb_movie[YEAR],
            release_date=release_date.date,
            release_date_notes=release_date.notes,
            directors=directors,
            writers=writers,
            cast=cast,
        )


def info_for_title(
    title_imdb_id: str,
) -> TitleDetail:
    return TitleDetail.from_imdb_id(title_imdb_id)


def credits_for_person(
    person_imdb_id: str, credit_key: str
) -> Sequence[CreditForPerson]:
    imdb_person = imdb_scraper.get_person(person_imdb_id[2:])
    filmography = imdb_person["filmography"]

    if credit_key == "performer":
        filmography["performer"] = filmography.pop("actor", [],) + filmography.pop(
            "actress",
            [],
        )

    credit_list: List[CreditForPerson] = []

    for imdb_movie in reversed(filmography.get(credit_key, [])):
        if credit_key == "writer":
            if not WritingCreditForTitle.credit_is_valid(imdb_movie):
                continue

        credit_list.append(CreditForPerson.from_imdb_movie(imdb_movie))

    return credit_list
