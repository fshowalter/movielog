import os
from dataclasses import asdict, dataclass
from datetime import date
from glob import glob
from typing import Any, Dict, List, Optional, Sequence, Set

from slugify import slugify

from movielog import db, imdb_http, yaml_file
from movielog.logger import logger

TABLE_NAME = "release_dates"
FOLDER_PATH = "release_dates"


@dataclass
class ReleaseDate(yaml_file.Movie):
    release_date: date
    notes: Optional[str]

    @classmethod
    def from_yaml_object(
        cls, file_path: str, yaml_object: Dict[str, Any]
    ) -> "ReleaseDate":
        title, year = cls.split_title_and_year(yaml_object["title"])

        return cls(
            imdb_id=yaml_object["imdb_id"],
            title=title,
            year=year,
            release_date=yaml_object["release_date"],
            notes=yaml_object["notes"],
            file_path=file_path,
        )

    def generate_slug(self) -> str:
        return str(slugify(self.title_with_year))

    @classmethod
    def folder_path(cls) -> str:
        return FOLDER_PATH

    def log_save(self) -> None:
        logger.log(
            "Wrote release date {}: {} ({}).",
            self.file_path,
            self.release_date,
            self.notes,
        )

    def as_yaml(self) -> Dict[str, Any]:
        return {
            "imdb_id": self.imdb_id,
            "title": self.title_with_year,
            "release_date": self.release_date,
            "notes": self.notes,
        }

    @classmethod
    def from_imdb_id(cls, imdb_id: str) -> "ReleaseDate":
        imdb_http_release_date = imdb_http.release_date_for_title(imdb_id)

        return ReleaseDate(
            imdb_id=imdb_id,
            title=imdb_http_release_date.title,
            year=int(imdb_http_release_date.year),
            release_date=imdb_http_release_date.release_date,
            notes=imdb_http_release_date.notes,
            file_path=None,
        )


class ReleaseDatesTable(db.Table):
    table_name = TABLE_NAME

    recreate_ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "{0}" (
            "movie_imdb_id" varchar(255) NOT NULL
                REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "release_date" TEXT NOT NULL,
            "notes" TEXT,
            PRIMARY KEY (movie_imdb_id));
        """

    @classmethod
    def insert_release_dates(cls, release_dates: Sequence[ReleaseDate]) -> None:
        ddl = """
        INSERT INTO {0}(movie_imdb_id, release_date, notes)
        VALUES(:imdb_id, :release_date, :notes);
        """.format(
            cls.table_name
        )

        cls.insert(
            ddl=ddl,
            parameter_seq=[asdict(release_date) for release_date in release_dates],
        )
        cls.add_index("movie_imdb_id")
        cls.validate(release_dates)


@logger.catch
def update(imdb_ids: List[str]) -> None:
    logger.log("==== Begin updating {}...", TABLE_NAME)

    ReleaseDatesTable.recreate()

    release_dates: List[ReleaseDate] = []

    existing_imdb_ids: Set[str] = set()

    for yaml_file_path in glob(os.path.join(FOLDER_PATH, "*.yml")):
        release_date = ReleaseDate.from_file_path(yaml_file_path)
        existing_imdb_ids.add(release_date.imdb_id)
        release_dates.append(release_date)

    for imdb_id in set(imdb_ids) - existing_imdb_ids:
        release_date = ReleaseDate.from_imdb_id(imdb_id)
        release_date.save()
        release_dates.append(release_date)

    ReleaseDatesTable.insert_release_dates(release_dates)
