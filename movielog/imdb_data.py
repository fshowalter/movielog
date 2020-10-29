import os
from dataclasses import asdict, dataclass
from datetime import date
from glob import glob
from typing import Any, Dict, List, Optional, Sequence, Set

from slugify import slugify

from movielog import db, humanize, imdb_http, yaml_file
from movielog.logger import logger

WRITING_CREDITS_TABLE_NAME = "writing_credits"
DIRECTING_CREDITS_TABLE_NAME = "directing_credits"
PERFORMING_CREDITS_TABLE_NAME = "performing_credits"
FOLDER_PATH = "data"
PERSON_IMDB_ID = "person_imdb_id"
SEQUENCE = "sequence"
NAME = "name"
NOTES = "notes"
IMDB_ID = "imdb_id"
RELEASE_DATES_TABLE_NAME = "release_dates"
MOVIE_IMDB_ID = "movie_imdb_id"
UPDATE_MESSAGE = "==== Begin updating {}..."


@dataclass
class Credit(object):
    movie_imdb_id: str
    person_imdb_id: str
    person_name: str
    sequence: int
    notes: Optional[str]


@dataclass
class DirectingCredit(Credit):
    def as_dict(self) -> Dict[str, Optional[str]]:
        return {
            SEQUENCE: str(self.sequence),
            MOVIE_IMDB_ID: self.movie_imdb_id,
            PERSON_IMDB_ID: self.person_imdb_id,
            NAME: self.person_name,
            NOTES: self.notes,
        }

    @classmethod
    def from_imdb_http_credit(
        cls, imdb_http_credit: imdb_http.DirectingCreditForTitle
    ) -> "DirectingCredit":
        return cls(
            movie_imdb_id=imdb_http_credit.movie_imdb_id,
            person_imdb_id=imdb_http_credit.person_imdb_id,
            person_name=imdb_http_credit.name,
            sequence=imdb_http_credit.sequence,
            notes=imdb_http_credit.notes,
        )

    @classmethod
    def from_yaml(
        cls, movie_imdb_id: str, yaml_object: Dict[str, Any]
    ) -> "DirectingCredit":
        return cls(
            movie_imdb_id=movie_imdb_id,
            person_imdb_id=yaml_object[PERSON_IMDB_ID],
            person_name=yaml_object[NAME],
            sequence=yaml_object[SEQUENCE],
            notes=yaml_object[NOTES],
        )

    def as_yaml(self) -> Any:
        return {
            SEQUENCE: self.sequence,
            PERSON_IMDB_ID: self.person_imdb_id,
            NAME: self.person_name,
            NOTES: self.notes,
        }


@dataclass
class WritingCredit(Credit):
    group_id: int

    def as_dict(self) -> Dict[str, Optional[str]]:
        return {
            "group_id": str(self.group_id),
            SEQUENCE: str(self.sequence),
            MOVIE_IMDB_ID: self.movie_imdb_id,
            PERSON_IMDB_ID: self.person_imdb_id,
            NAME: self.person_name,
            NOTES: self.notes,
        }

    @classmethod
    def from_imdb_http_credit(
        cls, imdb_http_credit: imdb_http.WritingCreditForTitle
    ) -> "WritingCredit":
        return cls(
            movie_imdb_id=imdb_http_credit.movie_imdb_id,
            person_imdb_id=imdb_http_credit.person_imdb_id,
            person_name=imdb_http_credit.name,
            sequence=imdb_http_credit.sequence,
            group_id=imdb_http_credit.group,
            notes=imdb_http_credit.notes,
        )

    @classmethod
    def from_yaml(
        cls, movie_imdb_id: str, yaml_object: Dict[str, Any]
    ) -> "WritingCredit":
        return cls(
            movie_imdb_id=movie_imdb_id,
            person_imdb_id=yaml_object[PERSON_IMDB_ID],
            person_name=yaml_object[NAME],
            sequence=yaml_object[SEQUENCE],
            notes=yaml_object[NOTES],
            group_id=yaml_object["group_id"],
        )

    def as_yaml(self) -> Any:
        return {
            "group_id": self.group_id,
            SEQUENCE: self.sequence,
            PERSON_IMDB_ID: self.person_imdb_id,
            NAME: self.person_name,
            NOTES: self.notes,
        }


@dataclass
class CastCredit(Credit):
    roles: List[str]

    @property
    def role_string(self) -> str:
        return " / ".join(self.roles)

    def as_dict(self) -> Dict[str, Optional[str]]:
        return {
            SEQUENCE: str(self.sequence),
            MOVIE_IMDB_ID: self.movie_imdb_id,
            PERSON_IMDB_ID: self.person_imdb_id,
            NAME: self.person_name,
            "role_string": self.role_string,
            NOTES: self.notes,
        }

    @classmethod
    def from_imdb_http_cast_credit(
        cls, imdb_http_cast_credit: imdb_http.CastCreditForTitle
    ) -> "CastCredit":
        return cls(
            movie_imdb_id=imdb_http_cast_credit.movie_imdb_id,
            person_imdb_id=imdb_http_cast_credit.person_imdb_id,
            person_name=imdb_http_cast_credit.name,
            sequence=imdb_http_cast_credit.sequence,
            roles=imdb_http_cast_credit.roles,
            notes=imdb_http_cast_credit.notes,
        )

    @classmethod
    def from_yaml(cls, movie_imdb_id: str, yaml_object: Dict[str, Any]) -> "CastCredit":
        return cls(
            movie_imdb_id=movie_imdb_id,
            person_imdb_id=yaml_object[PERSON_IMDB_ID],
            person_name=yaml_object[NAME],
            sequence=yaml_object[SEQUENCE],
            roles=yaml_object["roles"],
            notes=yaml_object[NOTES],
        )

    def as_yaml(self) -> Any:
        return {
            SEQUENCE: self.sequence,
            PERSON_IMDB_ID: self.person_imdb_id,
            NAME: self.person_name,
            "roles": self.roles,
            NOTES: self.notes,
        }


@dataclass
class Movie(yaml_file.Movie):
    performing_credits: List[CastCredit]
    directing_credits: List[DirectingCredit]
    writing_credits: List[WritingCredit]
    release_date: date
    release_date_notes: Optional[str]

    @classmethod
    def parse_directing_credits(
        cls, yaml_object: Dict[str, Any]
    ) -> List[DirectingCredit]:
        credit_list: List[DirectingCredit] = []

        for yaml_credit in yaml_object.get("directors", []):
            credit_list.append(
                DirectingCredit.from_yaml(yaml_object[IMDB_ID], yaml_credit)
            )

        return credit_list

    @classmethod
    def parse_writing_credits(cls, yaml_object: Dict[str, Any]) -> List[WritingCredit]:
        credit_list: List[WritingCredit] = []

        for yaml_credit in yaml_object.get("writers", []):
            credit_list.append(
                WritingCredit.from_yaml(yaml_object[IMDB_ID], yaml_credit)
            )

        return credit_list

    @classmethod
    def parse_cast_credits(cls, yaml_object: Dict[str, Any]) -> List[CastCredit]:
        credit_list: List[CastCredit] = []

        for yaml_credit in yaml_object.get("cast", []):
            credit_list.append(CastCredit.from_yaml(yaml_object[IMDB_ID], yaml_credit))

        return credit_list

    @classmethod
    def from_yaml_object(cls, file_path: str, yaml_object: Dict[str, Any]) -> "Movie":
        title, year = cls.split_title_and_year(yaml_object["title"])

        directing_credits: List[DirectingCredit] = cls.parse_directing_credits(
            yaml_object
        )
        writing_credits: List[WritingCredit] = cls.parse_writing_credits(yaml_object)
        performing_credits: List[CastCredit] = cls.parse_cast_credits(yaml_object)

        return cls(
            imdb_id=yaml_object[IMDB_ID],
            title=title,
            year=year,
            directing_credits=directing_credits,
            writing_credits=writing_credits,
            performing_credits=performing_credits,
            file_path=file_path,
            release_date=yaml_object["release_date"],
            release_date_notes=yaml_object["release_date_notes"],
        )

    def generate_slug(self) -> str:
        return str(slugify(self.title_with_year))

    @classmethod
    def folder_path(cls) -> str:
        return FOLDER_PATH

    def log_save(self) -> None:
        directing_credits_length = humanize.intcomma(len(self.directing_credits))
        writing_credits_length = humanize.intcomma(len(self.writing_credits))
        cast_credits_length = humanize.intcomma(len(self.performing_credits))
        logger.log(
            "Wrote {} with {} directing credits, {} writing credits, and {} cast credits.",
            self.file_path,
            directing_credits_length,
            writing_credits_length,
            cast_credits_length,
        )

    def as_yaml(self) -> Dict[str, Any]:
        return {
            IMDB_ID: self.imdb_id,
            "title": self.title_with_year,
            "release_date": self.release_date,
            "release_date_notes": self.release_date_notes,
            "directors": [
                directing_credit.as_yaml()
                for directing_credit in self.directing_credits
            ],
            "writers": [
                writing_credit.as_yaml() for writing_credit in self.writing_credits
            ],
            "cast": [
                performing_credit.as_yaml()
                for performing_credit in self.performing_credits
            ],
        }

    @classmethod
    def parse_existing_yaml_files(cls) -> List["Movie"]:
        movies: List["Movie"] = []

        for yaml_file_path in glob(os.path.join(FOLDER_PATH, "*.yml")):
            movies.append(cls.from_file_path(yaml_file_path))

        return movies

    @classmethod
    def from_imdb_id(cls, imdb_id: str) -> "Movie":
        movie_info = imdb_http.info_for_title(imdb_id)

        directing_credits = [
            DirectingCredit.from_imdb_http_credit(directing_credit)
            for directing_credit in movie_info.directors
        ]

        writing_credits = [
            WritingCredit.from_imdb_http_credit(writing_credit)
            for writing_credit in movie_info.writers
        ]

        performing_credits = [
            CastCredit.from_imdb_http_cast_credit(cast_credit)
            for cast_credit in movie_info.cast
        ]

        return Movie(
            imdb_id=imdb_id,
            title=movie_info.title,
            year=int(movie_info.year),
            directing_credits=directing_credits,
            writing_credits=writing_credits,
            performing_credits=performing_credits,
            file_path=None,
            release_date=movie_info.release_date,
            release_date_notes=movie_info.release_date_notes,
        )


class DirectingCreditsTable(db.Table):
    table_name = DIRECTING_CREDITS_TABLE_NAME

    recreate_ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "{0}" (
            "movie_imdb_id" varchar(255) NOT NULL
                REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "person_imdb_id" varchar(255) NOT NULL
                REFERENCES people(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "sequence" INT NOT NULL,
            "notes" TEXT,
            PRIMARY KEY (movie_imdb_id, person_imdb_id, notes));
        """

    @classmethod
    def insert_credits(cls, credit_items: List[DirectingCredit]) -> None:
        ddl = """
        INSERT INTO {0} (movie_imdb_id, person_imdb_id, sequence, notes)
        VALUES(:movie_imdb_id, :person_imdb_id, :sequence, :notes);
        """.format(
            cls.table_name
        )

        parameter_seq = [credit.as_dict() for credit in credit_items]

        cls.insert(ddl=ddl, parameter_seq=parameter_seq)
        cls.add_index("person_imdb_id")
        cls.validate(credit_items)


class WritingCreditsTable(db.Table):
    table_name = WRITING_CREDITS_TABLE_NAME

    recreate_ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "{0}" (
            "movie_imdb_id" varchar(255) NOT NULL
                REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "person_imdb_id" varchar(255) NOT NULL
                REFERENCES people(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "group_id" INT NOT NULL,
            "sequence" INT NOT NULL,
            "notes" TEXT,
            PRIMARY KEY (movie_imdb_id, person_imdb_id, group_id, notes));
        """

    @classmethod
    def insert_credits(cls, credit_items: List[WritingCredit]) -> None:
        ddl = """
        INSERT INTO {0} (movie_imdb_id, person_imdb_id, group_id, sequence, notes)
        VALUES(:movie_imdb_id, :person_imdb_id, :group_id, :sequence, :notes);
        """.format(
            cls.table_name
        )

        parameter_seq = [credit.as_dict() for credit in credit_items]

        cls.insert(ddl=ddl, parameter_seq=parameter_seq)
        cls.add_index("person_imdb_id")
        cls.validate(credit_items)


class PerformingCreditsTable(db.Table):
    table_name = PERFORMING_CREDITS_TABLE_NAME

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
    def insert_performing_credits(
        cls, performing_credits: Sequence[CastCredit]
    ) -> None:
        ddl = """
        INSERT INTO {0}(movie_imdb_id, person_imdb_id, sequence, roles, notes)
        VALUES(:movie_imdb_id, :person_imdb_id, :sequence, :role_string, :notes);
        """.format(
            cls.table_name
        )

        cls.insert(
            ddl=ddl, parameter_seq=[credit.as_dict() for credit in performing_credits]
        )
        cls.add_index("movie_imdb_id")
        cls.add_index(PERSON_IMDB_ID)
        cls.validate(performing_credits)


class ReleaseDatesTable(db.Table):
    table_name = RELEASE_DATES_TABLE_NAME

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
    def insert_release_dates(cls, movies: List[Movie]) -> None:
        ddl = """
        INSERT INTO {0}(movie_imdb_id, release_date, notes)
        VALUES(:imdb_id, :release_date, :release_date_notes);
        """.format(
            cls.table_name
        )

        cls.insert(
            ddl=ddl,
            parameter_seq=[asdict(movie) for movie in movies],
        )
        cls.add_index("movie_imdb_id")
        cls.validate(movies)


@logger.catch
def update(imdb_ids: List[str]) -> None:  # noqa: WPS213, WPS210
    logger.log("==== Begin updating {}...", "IMDb Credits and Release Dates")
    movies = Movie.parse_existing_yaml_files()
    directing_credits: List[DirectingCredit] = []
    writing_credits: List[WritingCredit] = []
    performing_credits: List[CastCredit] = []

    existing_imdb_ids: Set[str] = set()

    for movie in movies:
        existing_imdb_ids.add(movie.imdb_id)
        directing_credits.extend(movie.directing_credits)
        writing_credits.extend(movie.writing_credits)
        performing_credits.extend(movie.performing_credits)

    for imdb_id in set(imdb_ids) - existing_imdb_ids:
        new_movie = Movie.from_imdb_id(imdb_id)
        new_movie.save()
        movies.append(new_movie)
        directing_credits.extend(new_movie.directing_credits)
        writing_credits.extend(new_movie.writing_credits)
        performing_credits.extend(new_movie.performing_credits)

    logger.log(UPDATE_MESSAGE, DIRECTING_CREDITS_TABLE_NAME)
    DirectingCreditsTable.recreate()
    DirectingCreditsTable.insert_credits(directing_credits)

    logger.log(UPDATE_MESSAGE, WRITING_CREDITS_TABLE_NAME)
    WritingCreditsTable.recreate()
    WritingCreditsTable.insert_credits(writing_credits)

    logger.log(UPDATE_MESSAGE, PERFORMING_CREDITS_TABLE_NAME)
    PerformingCreditsTable.recreate()
    PerformingCreditsTable.insert_performing_credits(performing_credits)

    logger.log(UPDATE_MESSAGE, RELEASE_DATES_TABLE_NAME)
    ReleaseDatesTable.recreate()
    ReleaseDatesTable.insert_release_dates(movies)
