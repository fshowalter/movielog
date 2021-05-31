from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional, Sequence, TypedDict

from movielog import db

if TYPE_CHECKING:
    from movielog.moviedata.extended.movies import Movie

TABLE_NAME = "release_dates"

CREATE_DDL = """
  "movie_imdb_id" varchar(255) NOT NULL
      REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
  "release_date" TEXT NOT NULL,
  "notes" TEXT,
  PRIMARY KEY (movie_imdb_id)
"""

INSERT_DDL = """
  INSERT INTO {0}(movie_imdb_id, release_date, notes)
    VALUES(:movie_imdb_id, :release_date, :notes);
"""


class Row(TypedDict):
    movie_imdb_id: str
    release_date: date
    notes: Optional[str]


def reload(rows: Sequence[Row]) -> None:
    db.recreate_table(TABLE_NAME, CREATE_DDL)

    db.insert_into_table(
        table_name=TABLE_NAME,
        insert_ddl=INSERT_DDL.format(TABLE_NAME),
        rows=rows,
    )

    db.add_index(TABLE_NAME, "movie_imdb_id")

    db.validate_row_count(TABLE_NAME, len(rows))


def update(movies: list[Movie]) -> None:
    rows = [
        Row(
            movie_imdb_id=movie.imdb_id,
            release_date=movie.release_date,
            notes=movie.release_date_notes,
        )
        for movie in movies
    ]

    reload(rows)
