from dataclasses import asdict, dataclass
from typing import List, Optional

from movielog import db, humanize, imdb_s3_downloader, imdb_s3_extractor, movies
from movielog.logger import logger

FILE_NAME = "title.akas.tsv.gz"
TABLE_NAME = "aka_titles"


@dataclass  # noqa: WPS230
class AkaTitle(object):
    __slots__ = (
        "movie_imdb_id",
        "sequence",
        "title",
        "region",
        "language",
        "types",
        "attributes",
        "is_original_title",
    )
    movie_imdb_id: str
    sequence: int
    title: str
    region: Optional[str]
    language: Optional[str]
    types: Optional[str]
    attributes: Optional[str]
    is_original_title: Optional[str]

    @classmethod
    def from_imdb_s3_fields(cls, fields: List[Optional[str]]) -> "AkaTitle":
        return cls(
            movie_imdb_id=str(fields[0]),
            sequence=int(str(fields[1])),
            title=str(fields[2]),
            region=fields[3],
            language=fields[4],
            types=fields[5],
            attributes=fields[6],
            is_original_title=fields[7],
        )


class AkaTitlesTable(db.Table):
    table_name = TABLE_NAME

    recreate_ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "{0}" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            "movie_imdb_id" TEXT NOT NULL
                REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "sequence" INT NOT NULL,
            "title" TEXT NOT NULL,
            "region" TEXT,
            "language" TEXT,
            "types" TEXT,
            "attributes" TEXT,
            is_original_title BOOLEAN DEFAULT FALSE);
    """

    @classmethod
    def insert_aka_titles(cls, aka_titles: List[AkaTitle]) -> None:
        ddl = """
            INSERT INTO {0}(
              movie_imdb_id,
              sequence,
              title,
              region,
              language,
              types,
              attributes,
              is_original_title)
            VALUES(
                :movie_imdb_id,
                :sequence,
                :title,
                :region,
                :language,
                :types,
                :attributes,
                :is_original_title);""".format(
            cls.table_name
        )

        parameter_seq = [asdict(aka_title) for aka_title in aka_titles]

        cls.insert(ddl=ddl, parameter_seq=parameter_seq)
        cls.add_index("title")
        cls.validate(aka_titles)


def update() -> None:
    logger.log("==== Begin updating {} ...", TABLE_NAME)

    downloaded_file_path = imdb_s3_downloader.download(FILE_NAME)

    for _ in imdb_s3_extractor.checkpoint(downloaded_file_path):  # noqa: WPS122
        aka_titles = extract_aka_titles(downloaded_file_path)
        AkaTitlesTable.recreate()
        AkaTitlesTable.insert_aka_titles(aka_titles)


def extract_aka_titles(downloaded_file_path: str) -> List[AkaTitle]:
    title_ids = movies.title_ids()
    aka_titles: List[AkaTitle] = []

    for fields in imdb_s3_extractor.extract(downloaded_file_path):
        if fields[0] in title_ids:
            aka_titles.append(AkaTitle.from_imdb_s3_fields(fields))

    logger.log("Extracted {} {}.", humanize.intcomma(len(aka_titles)), TABLE_NAME)

    return aka_titles
