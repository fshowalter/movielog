import os
from dataclasses import dataclass
from glob import glob
from typing import Any, Dict, Iterable, List, Optional, Type, TypeVar

from slugify import slugify

from movielog import yaml_file

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
    year: int
    title: str
    notes: Optional[str] = None

    def as_yaml(self) -> Dict[str, Any]:
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
    def from_yaml_object(cls, yaml_object: Dict[str, Any]) -> "Title":
        return cls(
            imdb_id=str(yaml_object.get(IMDB_ID)),
            title=str(yaml_object.get("title")),
            year=int(str(yaml_object.get(YEAR))),
            notes=yaml_object.get("notes", None),
        )


WatchlistFileType = TypeVar("WatchlistFileType", bound="WatchlistFile")


@dataclass  # type: ignore
class WatchlistFile(yaml_file.Base):
    name: str
    imdb_id: Optional[str]
    titles: List[Title]
    frozen: bool

    def __init__(  # noqa: WPS211
        self,
        name: str,
        imdb_id: Optional[str] = None,
        file_path: Optional[str] = None,
        titles: Optional[List[Title]] = None,
        frozen: bool = False,
    ) -> None:
        self.imdb_id = imdb_id
        self.name = name
        self.file_path = file_path
        if not titles:
            titles = []
        self.titles = titles
        self.frozen = frozen

    @classmethod
    def from_yaml_object(
        cls: Type[WatchlistFileType], yaml_object: Dict[str, Any]
    ) -> WatchlistFileType:
        titles: List[Title] = []

        for yaml_title in yaml_object.get(TITLES, []):
            titles.append(Title.from_yaml_object(yaml_title))

        return cls(
            imdb_id=yaml_object.get(IMDB_ID),
            name=yaml_object[NAME],
            frozen=yaml_object.get(FROZEN, False),  # noqa: WPS425,
            titles=titles,
        )

    def as_yaml(self) -> Dict[str, Any]:
        if self.imdb_id:
            return {
                FROZEN: self.frozen,
                NAME: self.name,
                IMDB_ID: self.imdb_id,
                TITLES: [title.as_yaml() for title in self.titles],
            }

        return {
            FROZEN: self.frozen,
            NAME: self.name,
            TITLES: [title.as_yaml() for title in self.titles],
        }

    @classmethod
    def all_items(cls: Type[WatchlistFileType]) -> List[WatchlistFileType]:
        yaml_files_path = os.path.join(cls.folder_path(), "*.yml")

        return [
            cls.from_file_path(yaml_file_path)
            for yaml_file_path in sorted(glob(yaml_files_path))
        ]

    @classmethod
    def unfrozen_items(cls: Type[WatchlistFileType]) -> Iterable[WatchlistFileType]:
        yaml_files_path = os.path.join(cls.folder_path(), "*.yml")

        for yaml_file_path in sorted(glob(yaml_files_path)):
            watchlist_item = cls.from_file_path(yaml_file_path)

            if watchlist_item.frozen:
                continue

            yield watchlist_item

    def generate_slug(self) -> str:
        return str(slugify(self.name))
