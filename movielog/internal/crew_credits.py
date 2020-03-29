from dataclasses import asdict, dataclass
from typing import List, Optional, Sequence, Tuple

from movielog.internal import (
    db,
    humanize,
    imdb_s3_downloader,
    imdb_s3_extractor,
    movies,
    table_base,
)
from movielog.logger import logger

FILE_NAME = "title.crew.tsv.gz"
DIRECTING_CREDITS_TABLE_NAME = "directing_credits"
WRITING_CREDITS_TABLE_NAME = "writing_credits"


@dataclass
class CrewCredit(object):
    movie_imdb_id: str
    person_imdb_id: str
    sequence: str

    def __init__(self, movie_imdb_id: str, person_imdb_id: str, sequence: str) -> None:
        self.movie_imdb_id = movie_imdb_id
        self.person_imdb_id = person_imdb_id
        self.sequence = sequence


class CreditsTable(table_base.TableBase):
    def drop_and_create(self) -> None:
        ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "{0}" (
            "movie_imdb_id" varchar(255) NOT NULL
                REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "person_imdb_id" varchar(255) NOT NULL
                REFERENCES people(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "sequence" INT NOT NULL,
            PRIMARY KEY (movie_imdb_id, person_imdb_id));
        """.format(
            self.table_name
        )

        super().drop_and_create(ddl)

    def insert(self, credit_items: Sequence[CrewCredit]) -> None:
        ddl = """
        INSERT INTO {0} (movie_imdb_id, person_imdb_id, sequence)
        VALUES(:movie_imdb_id, :person_imdb_id, :sequence);
        """.format(
            self.table_name
        )

        parameter_seq = [asdict(credit) for credit in credit_items]

        super().insert(ddl=ddl, parameter_seq=parameter_seq)
        self.add_index("person_imdb_id")
        self.validate(credit_items)


def update() -> None:
    logger.log(
        "==== Begin updating {0} and {1}...",
        DIRECTING_CREDITS_TABLE_NAME,
        WRITING_CREDITS_TABLE_NAME,
    )

    downloaded_file_path = imdb_s3_downloader.download(FILE_NAME, db.DB_DIR)

    for _ in imdb_s3_extractor.checkpoint(downloaded_file_path):  # noqa: WPS122
        directing_credits, writing_credits = _extract_credits(downloaded_file_path)
        directing_credits_table = CreditsTable(DIRECTING_CREDITS_TABLE_NAME)
        directing_credits_table.drop_and_create()
        directing_credits_table.insert(directing_credits)
        writing_credits_table = CreditsTable(WRITING_CREDITS_TABLE_NAME)
        writing_credits_table.drop_and_create()
        writing_credits_table.insert(writing_credits)


def _extract_credits(
    downloaded_file_path: str,
) -> Tuple[List[CrewCredit], List[CrewCredit]]:
    title_ids = movies.title_ids()
    directing_credits: List[CrewCredit] = []
    writing_credits: List[CrewCredit] = []

    for fields in imdb_s3_extractor.extract(downloaded_file_path):
        title_id = fields[0]
        if title_id in title_ids:
            directing_credits.extend(_fields_to_credits(fields, 1))
            writing_credits.extend(_fields_to_credits(fields, 2))

    logger.log(
        "Extracted {0} {1}.",
        humanize.intcomma(len(directing_credits)),
        DIRECTING_CREDITS_TABLE_NAME,
    )
    logger.log(
        "Extracted {0} {1}.",
        humanize.intcomma(len(writing_credits)),
        WRITING_CREDITS_TABLE_NAME,
    )

    return (directing_credits, writing_credits)


def _fields_to_credits(
    fields: List[Optional[str]], credit_index: int
) -> List[CrewCredit]:
    crew_credits: List[CrewCredit] = []

    if fields[credit_index] is None:
        return crew_credits

    for sequence, person_imdb_id in enumerate(str(fields[credit_index]).split(",")):
        crew_credits.append(
            CrewCredit(
                movie_imdb_id=str(fields[0]),
                person_imdb_id=person_imdb_id,
                sequence=str(sequence),
            )
        )

    return crew_credits
