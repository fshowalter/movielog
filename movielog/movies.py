import os
from dataclasses import dataclass
from functools import lru_cache
from glob import glob
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set

from slugify import slugify

from movielog import (
    db,
    humanize,
    imdb_http,
    imdb_s3_downloader,
    imdb_s3_extractor,
    yaml_file,
)
from movielog.logger import logger

MOVIES_FILE_NAME = "title.basics.tsv.gz"
PRINCIPALS_FILE_NAME = "title.principals.tsv.gz"

TABLE_NAME = "movies"
FOLDER_PATH = "movie_countries"

IMDB_ID = "imdb_id"
TITLE = "title"

Whitelist = {
    "tt0116671",  # Jack Frost (1997) [V]
    "tt0148615",  # Play Motel (1979) [X]
    "tt1801096",  # Sexy Evil Genius (2013) [V]
    "tt0093135",  # Hack-O-Lantern (1988) [V]
}


@dataclass
class Movie(object):
    __slots__ = (
        "imdb_id",
        "title",
        "original_title",
        "year",
        "runtime_minutes",
        "principal_cast",
    )
    imdb_id: str
    title: str
    original_title: str
    year: str
    runtime_minutes: str
    principal_cast: List["Principal"]

    @classmethod
    def from_imdb_s3_fields(cls, fields: List[Optional[str]]) -> "Movie":
        return Movie(
            imdb_id=str(fields[0]),
            title=str(fields[2]),
            original_title=str(fields[3]),
            year=str(fields[5]),
            runtime_minutes=str(fields[7]),
            principal_cast=[],
        )

    @classmethod
    def from_imdb_s3_file(cls, file_path: str) -> "MovieCollection":
        movies: Dict[str, Movie] = {}

        for fields in imdb_s3_extractor.extract(file_path):
            imdb_id = str(fields[0])
            if imdb_id in Whitelist or cls.s3_fields_are_valid(fields):
                movies[imdb_id] = cls.from_imdb_s3_fields(fields)

        logger.log("Extracted {} {}.", humanize.intcomma(len(movies)), TABLE_NAME)

        return MovieCollection(movies)

    @classmethod
    def s3_fields_are_valid(cls, fields: List[Optional[str]]) -> bool:
        if fields[1] != "movie":
            return False
        if fields[4] == "1":
            return False
        if fields[5] is None:
            return False

        genres = set(str(fields[8]).split(","))
        if "Documentary" in genres:
            return False

        return True

    def as_dict(self) -> Dict[str, Optional[str]]:
        return {
            IMDB_ID: self.imdb_id,
            TITLE: self.title,
            "original_title": self.original_title,
            "year": self.year,
            "runtime_minutes": self.runtime_minutes,
            "principal_cast_ids": ",".join(self.principal_cast_ids),
        }

    @property
    def principal_cast_ids(self) -> Sequence[str]:
        return [
            principal.person_imdb_id
            for principal in sorted(
                self.principal_cast, key=lambda principal: principal.sequence
            )
        ]


@dataclass
class Countries(yaml_file.Movie):
    names: List[str]

    @classmethod
    def from_yaml_object(
        cls, file_path: str, yaml_object: Dict[str, Any]
    ) -> "Countries":
        title, year = cls.split_title_and_year(yaml_object[TITLE])

        return cls(
            imdb_id=yaml_object[IMDB_ID],
            title=title,
            year=year,
            names=yaml_object["names"],
            file_path=file_path,
        )

    def generate_slug(self) -> str:
        return str(slugify(self.title_with_year))

    @classmethod
    def folder_path(cls) -> str:
        return FOLDER_PATH

    def as_yaml(self) -> Dict[str, Any]:
        return {
            IMDB_ID: self.imdb_id,
            TITLE: self.title_with_year,
            "names": self.names,
        }

    @classmethod
    def from_imdb_id(cls, imdb_id: str) -> "Countries":
        detail = imdb_http.countries_for_title(imdb_id)

        return cls(
            imdb_id=imdb_id,
            title=detail.title,
            year=detail.year,
            names=detail.countries,
            file_path=None,
        )


@dataclass
class MovieCollection(object):
    movie_map: Dict[str, Movie]

    def append_principal_cast(self, downloaded_file_path: str) -> None:
        principals = 0
        for fields in imdb_s3_extractor.extract(downloaded_file_path):
            movie_imdb_id = str(fields[0])
            if movie_imdb_id not in self.movie_map:
                continue
            if fields[3] not in {"actor", "actress"}:
                continue

            self.movie_map[movie_imdb_id].principal_cast.append(
                Principal.from_imdb_s3_fields(fields)
            )
            principals += 1

        logger.log("Extracted {} {}.", humanize.intcomma(principals), "cast principals")

        removed = 0

        for movie in list(self.movie_map.values()):
            if not movie.principal_cast_ids:
                del self.movie_map[movie.imdb_id]  # noqa: WPS420
                removed += 1

        logger.log(
            "Removed {} {} with {}.",
            humanize.intcomma(removed),
            "movies",
            "no principal cast",
        )

    def as_list(self) -> Sequence[Movie]:
        return list(self.movie_map.values())


@dataclass
class Principal(object):
    __slots__ = (
        "movie_imdb_id",
        "person_imdb_id",
        "sequence",
        "category",
        "job",
        "characters",
    )
    movie_imdb_id: str
    person_imdb_id: str
    sequence: int
    category: Optional[str]
    job: Optional[str]
    characters: Optional[str]

    @classmethod
    def from_imdb_s3_fields(cls, fields: List[Optional[str]]) -> "Principal":
        return cls(
            movie_imdb_id=str(fields[0]),
            sequence=int(str(fields[1])),
            person_imdb_id=str(fields[2]),
            category=fields[3],
            job=fields[4],
            characters=fields[5],
        )


class MoviesTable(db.Table):
    table_name = TABLE_NAME

    recreate_ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "{0}" (
            "imdb_id" TEXT PRIMARY KEY NOT NULL,
            "title" TEXT NOT NULL,
            "original_title" TEXT,
            "year" INT NOT NULL,
            "runtime_minutes" INT,
            "principal_cast_ids" TEXT);
    """

    @classmethod
    def insert_movies(cls, movies: Sequence[Movie]) -> None:
        ddl = """
          INSERT INTO {0}(imdb_id, title, original_title, year, runtime_minutes, principal_cast_ids)
          VALUES(:imdb_id, :title, :original_title, :year, :runtime_minutes, :principal_cast_ids);
        """.format(
            cls.table_name
        )
        cls.insert(ddl=ddl, parameter_seq=[movie.as_dict() for movie in movies])
        cls.add_index("title")
        cls.validate(movies)


def update() -> None:
    logger.log("==== Begin updating {}...", TABLE_NAME)

    movies_file_path = imdb_s3_downloader.download(MOVIES_FILE_NAME)
    principals_file_path = imdb_s3_downloader.download(PRINCIPALS_FILE_NAME)

    for _ in imdb_s3_extractor.checkpoint(movies_file_path):  # noqa: WPS122
        movies = Movie.from_imdb_s3_file(movies_file_path)
        movies.append_principal_cast(principals_file_path)

        MoviesTable.recreate()
        MoviesTable.insert_movies(movies.as_list())
        title_ids.cache_clear()


def update_countries(imdb_ids: Iterable[str]) -> None:
    logger.log("==== Begin updating {}...", "movie countries")

    existing_extra_info_ids: Set[str] = set()

    for yaml_file_path in glob(os.path.join(FOLDER_PATH, "*.yml")):
        extra_info = Countries.from_file_path(yaml_file_path)
        existing_extra_info_ids.add(extra_info.imdb_id)

    for imdb_id in set(imdb_ids) - existing_extra_info_ids:
        extra_info = Countries.from_imdb_id(imdb_id)
        extra_info.save()


@lru_cache(1)
def title_ids() -> Set[str]:
    with db.connect() as connection:
        cursor = connection.cursor()
        cursor.row_factory = lambda cursor, row: row[0]
        return set(cursor.execute("select imdb_id from movies").fetchall())
