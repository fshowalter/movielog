from dataclasses import asdict, dataclass
from typing import List, Optional

from movielog import db, humanize, imdb_s3_downloader, imdb_s3_extractor, movies
from movielog.logger import logger

FILE_NAME = "title.principals.tsv.gz"
TABLE_NAME = "principals"


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


class PrincipalsTable(db.Table):
    table_name = TABLE_NAME

    recreate_ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "{0}" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            "movie_imdb_id" TEXT NOT NULL REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "person_imdb_id" TEXT NOT NULL REFERENCES people(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "sequence" INT NOT NULL,
            "category" TEXT,
            "job" TEXT,
            "characters" TEXT);
        """

    @classmethod
    def insert_principals(cls, principals: List[Principal]) -> None:
        ddl = """
            INSERT INTO "{0}" (
                movie_imdb_id,
                person_imdb_id,
                sequence,
                category,
                job,
                characters)
            VALUES (
                :movie_imdb_id,
                :person_imdb_id,
                :sequence,
                :category,
                :job,
                :characters)
        """

        parameter_seq = [asdict(principal) for principal in principals]

        cls.insert(ddl=ddl.format(cls.table_name), parameter_seq=parameter_seq)
        cls.add_index("category")
        cls.validate(principals)


def update() -> None:
    logger.log("==== Begin updating {} ...", TABLE_NAME)

    downloaded_file_path = imdb_s3_downloader.download(FILE_NAME)

    for _ in imdb_s3_extractor.checkpoint(downloaded_file_path):  # noqa: WPS122
        principals = extract_principals(downloaded_file_path)
        PrincipalsTable.recreate()
        PrincipalsTable.insert_principals(principals)


def extract_principals(downloaded_file_path: str) -> List[Principal]:
    title_ids = movies.title_ids()
    principals: List[Principal] = []

    for fields in imdb_s3_extractor.extract(downloaded_file_path):
        if (fields[0] in title_ids) and (fields[3] in {"actor", "actress"}):
            principals.append(Principal.from_imdb_s3_fields(fields))

    logger.log("Extracted {} {}.", humanize.intcomma(len(principals)), TABLE_NAME)

    return principals
