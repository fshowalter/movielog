from datetime import date
from typing import Protocol, Sequence, TypedDict

from movielog import db

TABLE_NAME = "viewings"

CREATE_DDL = """
  "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  "movie_imdb_id" TEXT NOT NULL REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
  "date" DATE NOT NULL,
  "sequence" INT NOT NULL,
  "venue" TEXT NOT NULL
"""

INSERT_DDL = """
  INSERT INTO {0}(movie_imdb_id, date, sequence, venue)
    VALUES(:movie_imdb_id, :date, :sequence, :venue);
"""


class Viewing(Protocol):
    sequence: int
    date: date
    imdb_id: str
    title: str
    venue: str


class Row(TypedDict):
    movie_imdb_id: str
    date: date
    sequence: int
    venue: str


def reload(rows: Sequence[Row]) -> None:
    db.recreate_table(TABLE_NAME, CREATE_DDL)

    db.insert_into_table(
        table_name=TABLE_NAME,
        insert_ddl=INSERT_DDL.format(TABLE_NAME),
        rows=rows,
    )

    db.add_index(TABLE_NAME, "movie_imdb_id")
    db.add_index(TABLE_NAME, "sequence")
    db.add_index(TABLE_NAME, "venue")

    db.validate_row_count(TABLE_NAME, len(rows))


def update(viewings: Sequence[Viewing]) -> None:
    reload(
        [
            Row(
                movie_imdb_id=viewing.imdb_id,
                date=viewing.date,
                sequence=viewing.sequence,
                venue=viewing.venue,
            )
            for viewing in viewings
        ]
    )
