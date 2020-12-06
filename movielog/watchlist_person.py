import abc
import json
import os
from dataclasses import asdict, dataclass
from glob import glob
from typing import Any, Dict, Iterable, List, Optional, Type, TypeVar

from slugify import slugify

from movielog import imdb_http
from movielog.logger import logger
from movielog.movies import title_ids as valid_title_ids

DIRECTORS_PATH = os.path.join("watchlist", "directors")
PERFORMERS_PATH = os.path.join("watchlist", "performers")
WRITERS_PATH = os.path.join("watchlist", "writers")

PersonType = TypeVar("PersonType", bound="Person")  # noqa: WPS111


@dataclass
class Movie(object):
    title: str
    year: int
    imdb_id: str
    notes: Optional[str] = None

    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> "Movie":
        return cls(
            imdb_id=json_object["imdb_id"],
            title=json_object["title"],
            notes=json_object["notes"],
            year=json_object["year"],
        )


@dataclass  # type: ignore
class Person(abc.ABC):
    frozen: bool
    name: str
    slug: str
    imdb_id: str
    movies: List[Movie]
    file_path: Optional[str]

    def __init__(
        self,
        name: str,
        imdb_id: str,
        frozen: bool = False,
        file_path: Optional[str] = None,
        movies: Optional[List[Movie]] = None,
        slug: Optional[str] = None,
    ) -> None:
        self.name = name
        self.imdb_id = imdb_id
        self.frozen = frozen
        self.slug = slug or slugify(name, replacements=[("'", "")])
        self.movies = movies or []
        self.file_path = file_path

    @classmethod
    @abc.abstractmethod
    def folder_path(cls) -> str:
        """ Implement behavior to return the folder path for this instance. """

    @classmethod
    @abc.abstractmethod
    def credit_key(cls) -> str:
        """ Implement behavior to return the credit key for this instance. """

    @classmethod
    def from_json_object(cls, file_path: str, json_object: Dict[str, Any]) -> "Person":
        movies: List[Movie] = []

        for json_movie_object in json_object["movies"]:
            movies.append(Movie.from_json_object(json_movie_object))

        return cls(
            imdb_id=json_object["imdb_id"],
            name=json_object["name"],
            frozen=json_object["frozen"],
            movies=movies,
            file_path=file_path,
            slug=json_object["slug"],
        )

    @classmethod
    def from_file_path(cls, file_path: str) -> "Person":
        json_object = None

        with open(file_path, "r") as json_file:
            json_object = json.load(json_file)

        return cls.from_json_object(file_path=file_path, json_object=json_object)

    @classmethod
    def all_items(cls) -> List["Person"]:
        file_paths = os.path.join(cls.folder_path(), "*.json")

        return [cls.from_file_path(file_path) for file_path in sorted(glob(file_paths))]

    def as_dict(self) -> Dict[str, Any]:
        person_dict = asdict(self)
        person_dict.pop("file_path", None)
        return person_dict

    def save(self) -> str:
        file_path = self.file_path

        if not file_path:
            file_path = os.path.join(
                type(self).folder_path(), "{0}.json".format(self.slug)
            )

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        with open(file_path, "w") as output_file:
            output_file.write(json.dumps(self.as_dict(), default=str, indent=2))

        self.file_path = file_path

        logger.log(
            "Wrote {} ({}) to {} with {} movies",
            self.name,
            self.imdb_id,
            self.file_path,
            len(self.movies),
        )

        return file_path


class Director(Person):
    @classmethod
    def folder_path(cls) -> str:
        return DIRECTORS_PATH

    @classmethod
    def credit_key(cls) -> str:
        return "director"


class Performer(Person):
    @classmethod
    def folder_path(cls) -> str:
        return PERFORMERS_PATH

    @classmethod
    def credit_key(cls) -> str:
        return "performer"


class Writer(Person):
    @classmethod
    def folder_path(cls) -> str:
        return WRITERS_PATH

    @classmethod
    def credit_key(cls) -> str:
        return "writer"


class CreditRefresher(object):
    @classmethod
    def refresh_person_credits(cls, person: Person) -> None:  # noqa: WPS231
        type_credit_key = type(person).credit_key()

        logger.log(
            "==== Begin refreshing {} credits for {}...",
            type_credit_key,
            person.name,
        )

        person.movies = []

        credits_for_person = imdb_http.credits_for_person(
            person.imdb_id, type_credit_key
        )

        for credit_for_person in credits_for_person:
            if credit_for_person.imdb_id not in valid_title_ids():
                cls.log_skip(
                    name=person.name,
                    year=credit_for_person.year,
                    title=credit_for_person.title,
                    reason=credit_for_person.notes,
                )
                continue
            if credit_for_person.in_production:
                cls.log_skip(
                    name=person.name,
                    year=credit_for_person.year,
                    title=credit_for_person.title,
                    reason="({0})".format(credit_for_person.in_production),
                )
                continue
            if credit_for_person.is_silent_film():
                cls.log_skip(
                    name=person.name,
                    year=credit_for_person.year,
                    title=credit_for_person.title,
                    reason="(silent film)",
                )
                continue

            person.movies.append(
                Movie(
                    imdb_id=credit_for_person.imdb_id,
                    title=credit_for_person.title,
                    year=credit_for_person.year,
                    notes=credit_for_person.notes,
                )
            )

        person.save()

    @classmethod
    def log_skip(
        cls,
        name: str,
        title: str,
        year: int,
        reason: str,
    ) -> None:
        logger.log(
            "Skipping {0} ({1}) for {2} {3}",
            title,
            year,
            name,
            reason,
        )


AddType = TypeVar("AddType", Director, Performer, Writer)


def add(cls: Type[AddType], imdb_id: str, name: str) -> AddType:
    watchlist_person = cls(imdb_id=imdb_id, name=name)
    watchlist_person.save()
    CreditRefresher.refresh_person_credits(watchlist_person)
    return watchlist_person


def all_items() -> Iterable[Person]:
    for person_type in (Director, Performer, Writer):
        for person in person_type.all_items():
            yield person


def refresh_credits() -> None:
    for person in all_items():
        if person.frozen:
            continue
        CreditRefresher.refresh_person_credits(person)
