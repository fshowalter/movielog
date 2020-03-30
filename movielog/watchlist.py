import abc
import operator
import os
import time
from dataclasses import asdict, dataclass
from glob import glob
from typing import (  # noqa: WPS235
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

import yaml
from slugify import slugify

from movielog import imdb_http, movies, watchlist_titles
from movielog.logger import logger

WATCHLIST_PATH = "watchlist"

NAME = "name"
FROZEN = "frozen"
TITLES = "titles"
IMDB_ID = "imdb_id"
EMPTY = ""
YEAR = "year"


@dataclass
class Title(object):
    imdb_id: str
    year: Union[str, int]
    title: str
    notes: Optional[str] = None

    def to_yaml(self) -> Dict[str, Any]:
        if self.notes:
            return {
                "title": self.title,
                "notes": self.notes,
                IMDB_ID: self.imdb_id,
                YEAR: self.year,
            }

        return {
            "title": self.title,
            IMDB_ID: self.imdb_id,
            YEAR: self.year,
        }

    @classmethod
    def from_imdb_http_movie(cls, imdb_movie: imdb_http.Movie) -> "Title":
        return cls(
            imdb_id=imdb_movie.imdb_id,
            title=imdb_movie.title,
            year=imdb_movie.year,
            notes=imdb_movie.notes,
        )

    @classmethod
    def from_yaml(cls, yaml_object: Dict[str, Any]) -> "Title":
        return cls(
            imdb_id=str(yaml_object.get(IMDB_ID)),
            title=str(yaml_object.get("title")),
            year=int(str(yaml_object.get(YEAR))),
            notes=yaml_object.get("notes", None),
        )


T = TypeVar("T", bound="Base")  # noqa: WPS111


class Base(abc.ABC):  # noqa: WPS214
    folder = EMPTY

    def __init__(
        self,
        name: str,
        file_path: Optional[str] = None,
        titles: Optional[List[Title]] = None,
        frozen: bool = False,
    ) -> None:
        self.name = name
        self.file_path = file_path
        if not titles:
            titles = []
        self.titles = titles
        self.frozen = frozen

    @abc.abstractmethod
    def save(self) -> str:
        """Writes this item to disk.

        Returns:
            str: The path of the written item.
        """
        return EMPTY

    @classmethod
    def folder_path(cls) -> str:
        return os.path.join(WATCHLIST_PATH, cls.folder)

    @classmethod
    @abc.abstractmethod
    def load(cls: Type[T], yaml_file_path: str) -> T:
        """Creates a new instance from a YAML file path.

        Args:
            yaml_file_path (str): Path to the yaml file.

        Returns:
            T: A new instance.
        """
        return cls(EMPTY)

    @classmethod
    def all_items(cls: Type[T]) -> List[T]:
        yaml_files_path = os.path.join(cls.folder_path(), "*.yml")

        return [cls.load(yaml_file_path) for yaml_file_path in glob(yaml_files_path)]

    @classmethod
    def unfrozen_items(cls: Type[T]) -> Iterable[T]:
        yaml_files_path = os.path.join(cls.folder_path(), "*.yml")

        for yaml_file_path in sorted(glob(yaml_files_path)):
            watchlist_item = cls.load(yaml_file_path)

            if watchlist_item.frozen:
                continue

            yield watchlist_item

    @abc.abstractmethod
    def to_yaml(self) -> Any:
        """Returns a yaml string representation of this instance.

        Returns:
            Any: This instance as a YAML string.
        """
        return EMPTY

    def write(self) -> str:
        file_path = self.file_path

        if not file_path:
            slug = slugify(self.name)
            file_path = os.path.join(self.__class__.folder_path(), f"{slug}.yml")
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))

        with open(file_path, "wb") as output_file:
            output_file.write(self.to_yaml())

        return file_path


class Collection(Base):
    folder = "collections"

    @classmethod
    def new(cls, name: str) -> "Collection":
        return cls(name)

    def add_title(self, imdb_id: str, title: str, year: int) -> Sequence[Title]:
        self.titles.append(Title(imdb_id=imdb_id, title=title, year=year,),)

        self.titles.sort(key=operator.attrgetter(YEAR))

        return self.titles

    def save(self) -> str:
        self.file_path = self.write()

        logger.log(
            "Wrote {} to {} with {} movies",
            self.name,
            self.file_path,
            len(self.titles),
        )

        return self.file_path

    def to_yaml(self) -> Any:
        return yaml.dump(
            {
                NAME: self.name,
                FROZEN: self.frozen,
                TITLES: [asdict(title) for title in self.titles],
            },
            encoding="utf-8",
            allow_unicode=True,
            default_flow_style=False,
        )

    @classmethod
    def load(cls, yaml_file_path: str) -> "Collection":
        yaml_object = None

        with open(yaml_file_path, "r") as yaml_file:
            yaml_object = yaml.safe_load(yaml_file)

        titles: List[Title] = []

        for yaml_title in yaml_object.get(TITLES, []):
            titles.append(Title.from_yaml(yaml_title))

        return cls(
            name=yaml_object[NAME],
            frozen=yaml_object.get(FROZEN, False),  # noqa: WPS425,
            titles=titles,
        )


def log_skip(imdb_movie: imdb_http.Movie, name: str, reason: str) -> None:
    logger.log(
        "Skipping {} ({}) for {} {}", imdb_movie.title, imdb_movie.year, name, reason,
    )


PersonType = TypeVar("PersonType", bound="PersonBase")  # noqa: WPS111


class PersonBase(Base):  # noqa: WPS214
    credit_key = EMPTY

    def __init__(  # noqa: WPS211
        self,
        imdb_id: str,
        name: str,
        file_path: Optional[str] = None,
        titles: Optional[List[Title]] = None,
        frozen: bool = False,
    ) -> None:
        self.imdb_id = imdb_id
        super().__init__(
            name=name, file_path=file_path, titles=titles, frozen=frozen,
        )

    def to_yaml(self) -> Any:
        return yaml.dump(
            {
                FROZEN: self.frozen,
                NAME: self.name,
                IMDB_ID: self.imdb_id,
                TITLES: [title.to_yaml() for title in self.titles],
            },
            encoding="utf-8",
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )

    def save(self) -> str:
        self.file_path = self.write()

        logger.log(
            "Wrote {} ({}) to {} with {} movies",
            self.name,
            self.imdb_id,
            self.file_path,
            len(self.titles),
        )

        return self.file_path

    def refresh_item_titles(self) -> None:  # noqa: WPS231
        imdb_person = imdb_http.Person(self.imdb_id)

        self.titles = []
        credit_key = self.__class__.credit_key

        logger.log(
            "==== Begin refreshing {} credits for {}...", credit_key, self.name,
        )
        for movie in reversed(imdb_person.filmography.get(credit_key, [])):
            imdb_movie = imdb_http.Movie.from_imdb_movie(movie)

            if imdb_movie.imdb_id not in movies.title_ids():
                log_skip(imdb_movie, imdb_person.name, imdb_movie.notes)
                continue
            if imdb_movie.is_silent:
                log_skip(imdb_movie, imdb_person.name, "(silent film)")
                continue
            if imdb_movie.in_production:
                log_skip(imdb_movie, imdb_person.name, imdb_movie.notes)
                continue

            self.titles.append(Title.from_imdb_http_movie(imdb_movie))
            time.sleep(1)

        self.save()

    @classmethod
    def refresh_all_item_titles(cls) -> None:
        for person_item in cls.unfrozen_items():
            person_item.refresh_item_titles()

    @classmethod
    def new(cls: Type[PersonType], imdb_id: str, name: str) -> PersonType:
        return cls(imdb_id, name)

    @classmethod
    def load(cls: Type[PersonType], yaml_file_path: str) -> PersonType:
        yaml_object = None

        with open(yaml_file_path, "r") as yaml_file:
            yaml_object = yaml.safe_load(yaml_file)

        titles: List[Title] = []

        for yaml_title in yaml_object.get(TITLES, []):
            titles.append(Title.from_yaml(yaml_title))

        return cls(
            imdb_id=yaml_object.get("id", yaml_object.get(IMDB_ID)),
            name=yaml_object[NAME],
            frozen=yaml_object.get(FROZEN, False),  # noqa: WPS425,
            titles=titles,
        )


class Director(PersonBase):
    folder = "directors"
    credit_key = "director"


class Performer(PersonBase):
    folder = "performers"
    credit_key = "performer"


class Writer(PersonBase):
    folder = "writers"
    credit_key = "writer"


def add_collection(name: str) -> Collection:
    collection_watchlist_item = Collection.new(name=name)
    collection_watchlist_item.save()
    return collection_watchlist_item


def update_collection(collection: Collection) -> Collection:
    collection.save()
    return collection


def add_director(imdb_id: str, name: str) -> Director:
    director_watchlist_item = Director.new(imdb_id=imdb_id, name=name)
    director_watchlist_item.save()
    director_watchlist_item.refresh_item_titles()
    return director_watchlist_item


def add_performer(imdb_id: str, name: str) -> Performer:
    performer_watchlist_item = Performer.new(imdb_id=imdb_id, name=name)
    performer_watchlist_item.save()
    performer_watchlist_item.refresh_item_titles()
    return performer_watchlist_item


def add_writer(imdb_id: str, name: str) -> Writer:
    writer_watchlist_item = Writer.new(imdb_id=imdb_id, name=name)
    writer_watchlist_item.save()
    writer_watchlist_item.refresh_item_titles()
    return writer_watchlist_item


def update_titles_for_people() -> None:
    Director.refresh_all_item_titles()
    Performer.refresh_all_item_titles()
    Writer.refresh_all_item_titles()
    watchlist_titles.update()
