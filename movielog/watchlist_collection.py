import json
import operator
import os
from dataclasses import asdict, dataclass
from glob import glob
from typing import Any, Dict, List, Optional, Sequence

from slugify import slugify

from movielog import humanize
from movielog.logger import logger

FOLDER_PATH = os.path.join("watchlist", "collections")


@dataclass
class Movie(object):
    title: str
    year: int
    imdb_id: str

    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> "Movie":
        return cls(
            imdb_id=json_object["imdb_id"],
            title=json_object["title"],
            year=json_object["year"],
        )


@dataclass
class Collection(object):
    name: str
    slug: str
    movies: List[Movie]
    file_path: Optional[str]

    def __init__(
        self,
        name: str,
        file_path: Optional[str] = None,
        movies: Optional[List[Movie]] = None,
        slug: Optional[str] = None,
    ) -> None:
        self.name = name
        self.slug = slug or slugify(name, replacements=[("'", "")])
        self.movies = movies or []
        self.file_path = file_path

    @classmethod
    def from_json_object(
        cls, file_path: str, json_object: Dict[str, Any]
    ) -> "Collection":
        movies: List[Movie] = []

        for json_movie_object in json_object["movies"]:
            movies.append(Movie.from_json_object(json_movie_object))

        return cls(
            name=json_object["name"],
            movies=movies,
            file_path=file_path,
            slug=json_object["slug"],
        )

    @classmethod
    def from_file_path(cls, file_path: str) -> "Collection":
        json_object = None

        with open(file_path, "r") as json_file:
            json_object = json.load(json_file)

        return cls.from_json_object(file_path=file_path, json_object=json_object)

    @classmethod
    def all_items(cls) -> List["Collection"]:
        logger.log("==== Begin reading {} from disk...", "watchlist collections")
        file_paths = os.path.join(FOLDER_PATH, "*.json")
        collections = [
            cls.from_file_path(file_path) for file_path in sorted(glob(file_paths))
        ]
        logger.log("Read {} {}.", humanize.intcomma(len(collections)), "collections")
        return collections

    def add_title(self, imdb_id: str, title: str, year: int) -> Sequence[Movie]:
        self.movies.append(Movie(imdb_id=imdb_id, title=title, year=year))

        self.movies.sort(key=operator.attrgetter("title"))

        return self.movies

    def as_dict(self) -> Dict[str, Any]:
        collection_dict = asdict(self)
        collection_dict.pop("file_path", None)
        return collection_dict

    def save(self) -> str:
        file_path = self.file_path

        if not file_path:
            file_path = os.path.join(FOLDER_PATH, "{0}.json".format(self.slug))

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        with open(file_path, "w") as output_file:
            output_file.write(json.dumps(self.as_dict(), default=str, indent=2))

        self.file_path = file_path

        logger.log(
            "Wrote {} to {} with {} movies",
            self.name,
            self.file_path,
            len(self.movies),
        )

        return file_path


def all_items() -> Sequence[Collection]:
    return Collection.all_items()


def add(name: str) -> Collection:
    collection = Collection(name=name)
    collection.save()
    return collection


def update(collection: Collection) -> Collection:
    collection.save()
    return collection
