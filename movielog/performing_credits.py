import os
from dataclasses import dataclass
from glob import glob
from typing import Any, Dict, List, Optional, Sequence, Set

from slugify import slugify

from movielog import db, humanize, imdb_http, yaml_file
from movielog.logger import logger

TABLE_NAME = "performing_credits"
FOLDER_PATH = "performing_credits"
PERSON_IMDB_ID = "person_imdb_id"


@dataclass
class Credit(object):
    movie_imdb_id: str
    person_imdb_id: str
    person_name: str
    sequence: int
    roles: List[str]
    notes: Optional[str]

    @property
    def role_string(self) -> str:
        return " / ".join(self.roles)

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "sequence": str(self.sequence),
            "movie_imdb_id": self.movie_imdb_id,
            PERSON_IMDB_ID: self.person_imdb_id,
            "name": self.person_name,
            "role_string": self.role_string,
            "notes": self.notes,
        }

    @classmethod
    def from_imdb_http_cast_credit(
        cls, imdb_http_cast_credit: imdb_http.CastCreditForTitle
    ) -> "Credit":
        return cls(
            movie_imdb_id=imdb_http_cast_credit.movie_imdb_id,
            person_imdb_id=imdb_http_cast_credit.person_imdb_id,
            person_name=imdb_http_cast_credit.name,
            sequence=imdb_http_cast_credit.sequence,
            roles=imdb_http_cast_credit.roles,
            notes=imdb_http_cast_credit.notes,
        )

    @classmethod
    def from_yaml(cls, movie_imdb_id: str, yaml_object: Dict[str, Any]) -> "Credit":
        return cls(
            movie_imdb_id=movie_imdb_id,
            person_imdb_id=yaml_object[PERSON_IMDB_ID],
            person_name=yaml_object["name"],
            sequence=yaml_object["sequence"],
            roles=yaml_object["roles"],
            notes=yaml_object["notes"],
        )

    def as_yaml(self) -> Any:
        return {
            "sequence": self.sequence,
            PERSON_IMDB_ID: self.person_imdb_id,
            "name": self.person_name,
            "roles": self.roles,
            "notes": self.notes,
        }


@dataclass
class Movie(yaml_file.Movie):
    performing_credits: List[Credit]

    @classmethod
    def from_yaml_object(cls, yaml_object: Dict[str, Any]) -> "Movie":
        title, year = cls.split_title_and_year(yaml_object["title"])

        performing_credits: List[Credit] = []

        for yaml_performing_credit in yaml_object.get("cast", []):
            performing_credits.append(
                Credit.from_yaml(yaml_object["imdb_id"], yaml_performing_credit)
            )

        return cls(
            imdb_id=yaml_object["imdb_id"],
            title=yaml_object["title"],
            year=yaml_object["year"],
            performing_credits=performing_credits,
            file_path=None,
        )

    def generate_slug(self) -> str:
        return str(slugify(self.title_with_year))

    @classmethod
    def folder_path(cls) -> str:
        return FOLDER_PATH

    def log_save(self) -> None:
        credits_length = humanize.intcomma(len(self.performing_credits))
        logger.log("Wrote {} with {} credits.", self.file_path, credits_length)

    def as_yaml(self) -> Dict[str, Any]:
        return {
            "imdb_id": self.imdb_id,
            "title": self.title_with_year,
            "cast": [
                performing_credit.as_yaml()
                for performing_credit in self.performing_credits
            ],
        }

    @classmethod
    def from_imdb_id(cls, imdb_id: str) -> "Movie":
        (movie_info, cast_credits) = imdb_http.cast_credits_for_title(imdb_id)

        performing_credits = [
            Credit.from_imdb_http_cast_credit(cast_credit)
            for cast_credit in cast_credits
        ]

        return Movie(
            imdb_id=imdb_id,
            title=movie_info.title,
            year=int(movie_info.year),
            performing_credits=performing_credits,
            file_path=None,
        )


class PerformingCreditsTable(db.Table):
    table_name = TABLE_NAME

    recreate_ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "{0}" (
            "movie_imdb_id" varchar(255) NOT NULL
                REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "person_imdb_id" varchar(255) NOT NULL
                REFERENCES people(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "sequence" INT NOT NULL,
            "roles" TEXT,
            "notes" TEXT,
            PRIMARY KEY (movie_imdb_id, person_imdb_id));
        """

    @classmethod
    def insert_performing_credits(cls, performing_credits: Sequence[Credit]) -> None:
        ddl = """
        INSERT INTO {0}(movie_imdb_id, person_imdb_id, sequence, roles, notes)
        VALUES(:movie_imdb_id, :person_imdb_id, :sequence, :role_string, :notes);
        """.format(
            cls.table_name
        )

        cls.insert(
            ddl=ddl, parameter_seq=[credit.to_dict() for credit in performing_credits]
        )
        cls.add_index("movie_imdb_id")
        cls.add_index(PERSON_IMDB_ID)
        cls.validate(performing_credits)


@logger.catch
def update(imdb_ids: List[str]) -> None:
    logger.log("==== Begin updating {}...", TABLE_NAME)

    PerformingCreditsTable.recreate()

    performing_credits: List[Credit] = []

    existing_imdb_ids: Set[str] = set()

    for yaml_file_path in glob(os.path.join(FOLDER_PATH, "*.yml")):
        movie = Movie.from_file_path(yaml_file_path)
        existing_imdb_ids.add(movie.imdb_id)
        performing_credits.extend(movie.performing_credits)

    for imdb_id in set(imdb_ids) - existing_imdb_ids:
        movie = Movie.from_imdb_id(imdb_id)
        movie.save()
        performing_credits.extend(movie.performing_credits)

    PerformingCreditsTable.insert_performing_credits(performing_credits)
