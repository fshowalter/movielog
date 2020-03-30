from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import Any, Dict, List, Mapping, Optional, Set

from movielog import db, humanize, imdb_s3_downloader, imdb_s3_extractor
from movielog.logger import logger

FILE_NAME = "title.basics.tsv.gz"
TABLE_NAME = "movies"
Whitelist = {
    "tt0116671",  # Jack Frost (1997) [V]
    "tt0148615",  # Play Motel (1979) [X]
    "tt1801096",  # Sexy Evil Genius (2013) [V]
    "tt0093135",  # Hack-O-Lantern (1988) [V]
}


class MovieError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


@dataclass
class Movie(object):
    __slots__ = ("imdb_id", "title", "is_original_title", "year", "runtime_minutes")
    imdb_id: str
    title: str
    is_original_title: bool
    year: str
    runtime_minutes: str

    @classmethod
    def from_imdb_s3_fields(cls, fields: List[Optional[str]]) -> "Movie":
        return Movie(
            imdb_id=str(fields[0]),
            title=str(fields[2]),
            is_original_title=bool(fields[3]),
            year=str(fields[5]),
            runtime_minutes=str(fields[7]),
        )

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "Movie":
        return Movie(
            imdb_id=str(row["imdb_id"]),
            title=str(row["title"]),
            is_original_title=bool(row["is_original_title"]),
            year=str(row["year"]),
            runtime_minutes=str(row["runtime_minutes"]),
        )


class MoviesTable(db.Table):
    table_name = TABLE_NAME

    recreate_ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "{0}" (
            "imdb_id" TEXT PRIMARY KEY NOT NULL,
            "title" TEXT NOT NULL,
            "is_original_title" BOOL,
            "year" INT NOT NULL,
            "runtime_minutes" INT);
    """

    @classmethod
    def insert_movies(cls, movies: List[Movie]) -> None:
        ddl = """
          INSERT INTO {0}(imdb_id, title, is_original_title, year, runtime_minutes)
          VALUES(:imdb_id, :title, :is_original_title, :year, :runtime_minutes);
        """.format(
            cls.table_name
        )
        cls.insert(ddl=ddl, parameter_seq=[asdict(movie) for movie in movies])
        cls.add_index("title")
        cls.validate(movies)


def update() -> None:
    logger.log("==== Begin updating {}...", TABLE_NAME)

    downloaded_file_path = imdb_s3_downloader.download(FILE_NAME)

    for _ in imdb_s3_extractor.checkpoint(downloaded_file_path):  # noqa: WPS122
        movies = _extract_movies(downloaded_file_path)
        MoviesTable.recreate()
        MoviesTable.insert_movies(list(movies.values()))
        title_ids.cache_clear()


@lru_cache(1)
def title_ids() -> Set[str]:
    with db.connect() as connection:
        cursor = connection.cursor()
        cursor.row_factory = lambda cursor, row: row[0]
        return set(cursor.execute("select imdb_id from movies").fetchall())


def _extract_movies(downloaded_file_path: str) -> Mapping[str, Movie]:
    movies: Dict[str, Movie] = {}

    for fields in imdb_s3_extractor.extract(downloaded_file_path):
        imdb_id = str(fields[0])
        if imdb_id in Whitelist or title_line_is_valid(fields):
            movies[imdb_id] = Movie.from_imdb_s3_fields(fields)

    logger.log("Extracted {} {}.", humanize.intcomma(len(movies)), TABLE_NAME)
    return movies


def title_line_is_valid(title_line: List[Optional[str]]) -> bool:
    if title_line[1] != "movie":
        return False
    if title_line[4] == "1":
        return False
    if title_line[5] is None:
        return False

    genres = set(str(title_line[8]).split(","))
    if "Documentary" in genres:
        return False

    return True
