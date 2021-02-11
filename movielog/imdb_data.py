import json
import os
from dataclasses import asdict, dataclass
from datetime import date
from glob import glob
from typing import Any, Dict, List, Optional, Sequence, Set

from slugify import slugify

from movielog import db, humanize, imdb_http
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
COUNTRIES_TABLE_NAME = "countries"
SORT_TITLES_TABLE_NAME = "sort_titles"
MOVIE_IMDB_ID = "movie_imdb_id"
UPDATE_MESSAGE = "==== Begin updating {}..."


@dataclass
class DirectingCredit(object):
    person_imdb_id: str
    name: str
    sequence: int
    notes: Optional[str]

    @classmethod
    def from_imdb_http_credit(
        cls, imdb_http_credit: imdb_http.DirectingCreditForTitle
    ) -> "DirectingCredit":
        return cls(
            person_imdb_id=imdb_http_credit.person_imdb_id,
            name=imdb_http_credit.name,
            sequence=imdb_http_credit.sequence,
            notes=imdb_http_credit.notes,
        )

    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> "DirectingCredit":
        return cls(
            person_imdb_id=json_object[PERSON_IMDB_ID],
            name=json_object[NAME],
            sequence=json_object[SEQUENCE],
            notes=json_object[NOTES],
        )


@dataclass
class WritingCredit(object):
    person_imdb_id: str
    name: str
    sequence: int
    notes: Optional[str]
    group_id: int

    @classmethod
    def from_imdb_http_credit(
        cls, imdb_http_credit: imdb_http.WritingCreditForTitle
    ) -> "WritingCredit":
        return cls(
            person_imdb_id=imdb_http_credit.person_imdb_id,
            name=imdb_http_credit.name,
            sequence=imdb_http_credit.sequence,
            group_id=imdb_http_credit.group,
            notes=imdb_http_credit.notes,
        )

    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> "WritingCredit":
        return cls(
            person_imdb_id=json_object[PERSON_IMDB_ID],
            name=json_object[NAME],
            sequence=json_object[SEQUENCE],
            notes=json_object[NOTES],
            group_id=json_object["group_id"],
        )


@dataclass
class PerformingCredit(object):
    person_imdb_id: str
    name: str
    sequence: int
    notes: Optional[str]
    roles: List[str]

    @property
    def role_string(self) -> str:
        return " / ".join(self.roles)

    @classmethod
    def from_imdb_http_cast_credit(
        cls, imdb_http_cast_credit: imdb_http.CastCreditForTitle
    ) -> "PerformingCredit":
        return cls(
            person_imdb_id=imdb_http_cast_credit.person_imdb_id,
            name=imdb_http_cast_credit.name,
            sequence=imdb_http_cast_credit.sequence,
            roles=imdb_http_cast_credit.roles,
            notes=imdb_http_cast_credit.notes,
        )

    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> "PerformingCredit":
        return cls(
            person_imdb_id=json_object[PERSON_IMDB_ID],
            name=json_object[NAME],
            sequence=json_object[SEQUENCE],
            roles=json_object["roles"],
            notes=json_object[NOTES],
        )

    def as_dict(self) -> Dict[str, Any]:
        credit_dict = asdict(self)
        credit_dict["role_string"] = self.role_string
        return credit_dict


@dataclass
class Movie(object):
    file_path: Optional[str]
    imdb_id: str
    sort_title: str
    performers: List[PerformingCredit]
    directors: List[DirectingCredit]
    writers: List[WritingCredit]
    release_date: date
    release_date_notes: Optional[str]
    countries: List[str]

    @classmethod
    def parse_directing_credits(
        cls, json_object: Dict[str, Any]
    ) -> List[DirectingCredit]:
        credit_list: List[DirectingCredit] = []

        for json_credit_object in json_object.get("directors", []):
            credit_list.append(DirectingCredit.from_json_object(json_credit_object))

        return credit_list

    @classmethod
    def parse_writing_credits(cls, json_object: Dict[str, Any]) -> List[WritingCredit]:
        credit_list: List[WritingCredit] = []

        for json_credit_object in json_object.get("writers", []):
            credit_list.append(WritingCredit.from_json_object(json_credit_object))

        return credit_list

    @classmethod
    def parse_cast_credits(cls, json_object: Dict[str, Any]) -> List[PerformingCredit]:
        credit_list: List[PerformingCredit] = []

        for json_credit_object in json_object.get("performers", []):
            credit_list.append(PerformingCredit.from_json_object(json_credit_object))

        return credit_list

    @classmethod
    def build_sort_title(cls, title: str) -> str:
        title_lower = title.lower()
        title_words = title.split(" ")
        lower_words = title_lower.split(" ")
        articles = set(["a", "an", "the"])

        if (len(title_words) > 1) and (lower_words[0] in articles):
            return "{0}".format(" ".join(title_words[1 : len(title_words)]))

        return title

    @classmethod
    def from_json_object(cls, file_path: str, json_object: Dict[str, Any]) -> "Movie":
        directing_credits: List[DirectingCredit] = cls.parse_directing_credits(
            json_object
        )
        writing_credits: List[WritingCredit] = cls.parse_writing_credits(json_object)
        performing_credits: List[PerformingCredit] = cls.parse_cast_credits(json_object)

        return cls(
            imdb_id=json_object[IMDB_ID],
            sort_title=json_object["sort_title"],
            directors=directing_credits,
            writers=writing_credits,
            performers=performing_credits,
            file_path=file_path,
            release_date=json_object["release_date"],
            release_date_notes=json_object["release_date_notes"],
            countries=json_object["countries"],
        )

    @classmethod
    def from_file_path(cls, file_path: str) -> "Movie":
        json_object = None

        with open(file_path, "r") as json_file:
            json_object = json.load(json_file)

        instance = cls.from_json_object(file_path=file_path, json_object=json_object)
        instance.file_path = file_path

        return instance

    @classmethod
    def load_existing_files(cls) -> List["Movie"]:
        movies: List["Movie"] = []

        for file_path in glob(os.path.join(FOLDER_PATH, "*.json")):
            movies.append(cls.from_file_path(file_path))

        return movies

    @classmethod
    def from_imdb_id(cls, imdb_id: str) -> "Movie":
        movie_info = imdb_http.info_for_title(imdb_id)

        directors = [
            DirectingCredit.from_imdb_http_credit(directing_credit)
            for directing_credit in movie_info.directors
        ]

        writers = [
            WritingCredit.from_imdb_http_credit(writing_credit)
            for writing_credit in movie_info.writers
        ]

        performers = [
            PerformingCredit.from_imdb_http_cast_credit(cast_credit)
            for cast_credit in movie_info.cast
        ]

        return Movie(
            imdb_id=imdb_id,
            sort_title=cls.build_sort_title(
                "{0} ({1})".format(movie_info.title, movie_info.year)
            ),
            directors=directors,
            writers=writers,
            performers=performers,
            file_path=None,
            release_date=movie_info.release_date,
            release_date_notes=movie_info.release_date_notes,
            countries=movie_info.countries,
        )

    def save(self) -> str:
        file_path = self.file_path

        if not file_path:
            file_path = os.path.join(
                FOLDER_PATH, "{0}.json".format(slugify(self.sort_title))
            )
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))

        with open(file_path, "w") as output_file:
            output_file.write(json.dumps(self.as_dict(), default=str, indent=2))

        self.file_path = file_path

        logger.log(
            "Wrote {} with {} directors, {} writers, and {} performers.",
            self.file_path,
            humanize.intcomma(len(self.directors)),
            humanize.intcomma(len(self.writers)),
            humanize.intcomma(len(self.performers)),
        )

        return file_path

    def as_dict(self) -> Dict[str, Any]:
        movie_dict = asdict(self)
        movie_dict.pop("file_path", None)
        return movie_dict


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
    def insert_credits(cls, movies: List[Movie]) -> None:
        ddl = """
        INSERT INTO {0} (movie_imdb_id, person_imdb_id, sequence, notes)
        VALUES(:movie_imdb_id, :person_imdb_id, :sequence, :notes);
        """

        credit_entries = [
            dict(asdict(credit), movie_imdb_id=movie.imdb_id)
            for movie in movies
            for credit in movie.directors
        ]

        cls.insert(ddl=ddl.format(cls.table_name), parameter_seq=credit_entries)
        cls.add_index("person_imdb_id")
        cls.validate(credit_entries)


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
    def insert_credits(cls, movies: List[Movie]) -> None:
        ddl = """
        INSERT INTO {0} (movie_imdb_id, person_imdb_id, group_id, sequence, notes)
        VALUES(:movie_imdb_id, :person_imdb_id, :group_id, :sequence, :notes);
        """

        credit_entries = [
            dict(asdict(credit), movie_imdb_id=movie.imdb_id)
            for movie in movies
            for credit in movie.writers
        ]

        cls.insert(ddl=ddl.format(cls.table_name), parameter_seq=credit_entries)
        cls.add_index("person_imdb_id")
        cls.validate(credit_entries)


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
    def insert_performing_credits(cls, movies: Sequence[Movie]) -> None:
        ddl = """
        INSERT INTO {0}(movie_imdb_id, person_imdb_id, sequence, roles, notes)
        VALUES(:movie_imdb_id, :person_imdb_id, :sequence, :role_string, :notes);
        """

        credit_entries = [
            dict(credit.as_dict(), movie_imdb_id=movie.imdb_id)
            for movie in movies
            for credit in movie.performers
        ]

        cls.insert(ddl=ddl.format(cls.table_name), parameter_seq=credit_entries)
        cls.add_index(MOVIE_IMDB_ID)
        cls.add_index(PERSON_IMDB_ID)
        cls.validate(credit_entries)


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
        """

        cls.insert(
            ddl=ddl.format(cls.table_name),
            parameter_seq=[asdict(movie) for movie in movies],
        )
        cls.add_index(MOVIE_IMDB_ID)
        cls.validate(movies)


class CountriesTable(db.Table):
    table_name = COUNTRIES_TABLE_NAME

    recreate_ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "{0}" (
            "movie_imdb_id" varchar(255) NOT NULL
                REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "country" TEXT NOT NULL,
            PRIMARY KEY (movie_imdb_id, country));
        """

    @classmethod
    def insert_countries(cls, movies: List[Movie]) -> None:
        ddl = """
        INSERT INTO {0}(movie_imdb_id, country)
        VALUES(:movie_imdb_id, :country);
        """

        countries = [
            {"movie_imdb_id": movie.imdb_id, "country": country}
            for movie in movies
            for country in movie.countries
        ]

        cls.insert(
            ddl=ddl.format(cls.table_name),
            parameter_seq=countries,
        )
        cls.add_index(MOVIE_IMDB_ID)
        cls.validate(countries)


class SortTitlesTable(db.Table):
    table_name = SORT_TITLES_TABLE_NAME

    recreate_ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "{0}" (
            "movie_imdb_id" varchar(255) NOT NULL
                REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "sort_title" TEXT NOT NULL,
            PRIMARY KEY (movie_imdb_id));
        """

    @classmethod
    def insert_sort_titles(cls, movies: List[Movie]) -> None:
        ddl = """
        INSERT INTO {0}(movie_imdb_id, sort_title)
        VALUES(:imdb_id, :sort_title);
        """

        cls.insert(
            ddl=ddl.format(cls.table_name),
            parameter_seq=[asdict(movie) for movie in movies],
        )
        cls.add_index(MOVIE_IMDB_ID)
        cls.validate(movies)


@logger.catch
def update(imdb_ids: Set[str]) -> None:  # noqa: WPS213
    logger.log(
        "==== Begin reading {}...",
        "existing IMDb data files in {0} folder".format(FOLDER_PATH),
    )
    movies = Movie.load_existing_files()
    logger.log("Read {} files.", len(movies))

    existing_credit_imdb_ids: Set[str] = set()

    for movie in movies:
        existing_credit_imdb_ids.add(movie.imdb_id)

    for imdb_id in set(imdb_ids) - existing_credit_imdb_ids:
        new_movie = Movie.from_imdb_id(imdb_id)
        new_movie.save()
        movies.append(new_movie)

    logger.log(UPDATE_MESSAGE, DIRECTING_CREDITS_TABLE_NAME)
    DirectingCreditsTable.recreate()
    DirectingCreditsTable.insert_credits(movies)

    logger.log(UPDATE_MESSAGE, WRITING_CREDITS_TABLE_NAME)
    WritingCreditsTable.recreate()
    WritingCreditsTable.insert_credits(movies)

    logger.log(UPDATE_MESSAGE, PERFORMING_CREDITS_TABLE_NAME)
    PerformingCreditsTable.recreate()
    PerformingCreditsTable.insert_performing_credits(movies)

    logger.log(UPDATE_MESSAGE, RELEASE_DATES_TABLE_NAME)
    ReleaseDatesTable.recreate()
    ReleaseDatesTable.insert_release_dates(movies)

    logger.log(UPDATE_MESSAGE, COUNTRIES_TABLE_NAME)
    CountriesTable.recreate()
    CountriesTable.insert_countries(movies)

    logger.log(UPDATE_MESSAGE, SORT_TITLES_TABLE_NAME)
    SortTitlesTable.recreate()
    SortTitlesTable.insert_sort_titles(movies)
