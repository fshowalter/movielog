from typing import TypedDict

from movielog.repository.datasets.dataset_title import DatasetTitle
from movielog.repository.db import db

TABLE_NAME = "titles"

CREATE_DDL = """
  "imdb_id" TEXT PRIMARY KEY NOT NULL,
  "imdb_votes" INT,
  "imdb_rating" FLOAT
"""

INSERT_DDL = """
  INSERT INTO {0}(
      imdb_id
    , imdb_votes
    , imdb_rating
    )
    VALUES(
      :imdb_id
    , :imdb_votes
    , :imdb_rating
    )
"""


class Row(TypedDict):
    imdb_id: str
    imdb_votes: int
    imdb_rating: float


def reload(titles: list[DatasetTitle]) -> None:
    db.recreate_table(TABLE_NAME, CREATE_DDL)

    db.insert_into_table(
        table_name=TABLE_NAME,
        insert_ddl=INSERT_DDL.format(TABLE_NAME),
        rows=[
            Row(
                imdb_id=title["imdb_id"],
                imdb_rating=title["imdb_rating"],
                imdb_votes=title["imdb_votes"],
            )
            for title in titles
        ],
    )

    db.add_index(TABLE_NAME, "imdb_id")

    db.validate_row_count(TABLE_NAME, len(titles))
