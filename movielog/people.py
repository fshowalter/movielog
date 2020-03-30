import re
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Set

from movielog import db, humanize, imdb_s3_downloader, imdb_s3_extractor, movies
from movielog.logger import logger

FILE_NAME = "name.basics.tsv.gz"
TABLE_NAME = "people"
NAME_REGEX = re.compile(r"^([^\s]*)\s(.*)$")


@dataclass  # noqa: WPS230
class Person(object):
    __slots__ = (
        "imdb_id",
        "full_name",
        "last_name",
        "first_name",
        "birth_year",
        "death_year",
        "primary_profession",
        "known_for_title_ids",
    )
    imdb_id: str
    full_name: str
    last_name: Optional[str]
    first_name: Optional[str]
    birth_year: Optional[str]
    death_year: Optional[str]
    primary_profession: Optional[str]
    known_for_title_ids: Optional[str]

    @classmethod
    def from_imdb_s3_fields(cls, fields: List[Optional[str]]) -> "Person":
        match = NAME_REGEX.split(str(fields[1]))
        if len(match) == 1:
            match = ["", match[0], "", ""]

        return cls(
            imdb_id=str(fields[0]),
            full_name=str(fields[1]),
            last_name=match[2],
            first_name=match[1],
            birth_year=fields[2],
            death_year=fields[3],
            primary_profession=fields[4],
            known_for_title_ids=fields[5],
        )


class PeopleTable(db.Table):
    table_name = TABLE_NAME
    recreate_ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "{0}" (
            "imdb_id" TEXT PRIMARY KEY NOT NULL,
            "full_name" varchar(255) NOT NULL,
            "last_name" varchar(255),
            "first_name" varchar(255),
            "birth_year" TEXT,
            "death_year" TEXT,
            "primary_profession" TEXT,
            "known_for_title_ids" TEXT);
    """

    @classmethod
    def insert_people(cls, people: List[Person]) -> None:
        ddl = """
            INSERT INTO {0}(
                imdb_id,
                full_name,
                last_name,
                first_name,
                birth_year,
                death_year,
                primary_profession,
                known_for_title_ids)
            VALUES(
                :imdb_id,
                :full_name,
                :last_name,
                :first_name,
                :birth_year,
                :death_year,
                :primary_profession,
                :known_for_title_ids)
        """.format(
            cls.table_name
        )

        cls.insert(ddl=ddl, parameter_seq=[asdict(person) for person in people])
        cls.add_index("full_name")
        cls.validate(people)


def update() -> None:
    logger.log("==== Begin updating {}...", TABLE_NAME)

    downloaded_file_path = imdb_s3_downloader.download(FILE_NAME)

    for _ in imdb_s3_extractor.checkpoint(downloaded_file_path):  # noqa: WPS122
        people = _extract_people(downloaded_file_path)
        PeopleTable.recreate()
        PeopleTable.insert_people(list(people.values()))


def _extract_people(downloaded_file_path: str) -> Dict[str, Person]:
    people: Dict[str, Person] = {}
    title_ids = movies.title_ids()

    for fields in imdb_s3_extractor.extract(downloaded_file_path):
        if _has_valid_known_for_title_ids(fields[5], title_ids):
            people[str(fields[0])] = Person.from_imdb_s3_fields(fields)

    logger.log("Extracted {} {}.", humanize.intcomma(len(people)), TABLE_NAME)
    return people


def _has_valid_known_for_title_ids(
    known_for_title_ids: Optional[str], valid_title_ids: Set[str],
) -> bool:
    if known_for_title_ids is None:
        return False

    for title_id in known_for_title_ids.split(","):
        if title_id in valid_title_ids:
            return True

    return False
