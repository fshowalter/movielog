from __future__ import annotations

from typing import TYPE_CHECKING, Sequence, TypedDict

from movielog import db

if TYPE_CHECKING:
    from movielog.moviedata.extended.movies import Movie

TABLE_NAME = "genres"

CREATE_DDL = """
  "movie_imdb_id" varchar(255) NOT NULL
      REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
  "genre" TEXT NOT NULL,
  PRIMARY KEY (movie_imdb_id, genre)
"""

INSERT_DDL = """
  INSERT INTO {0}(movie_imdb_id, genre)
    VALUES(:movie_imdb_id, :genre);
"""


class Row(TypedDict):
    movie_imdb_id: str
    genre: str


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
        Row(movie_imdb_id=movie.imdb_id, genre=genre)
        for movie in movies
        for genre in movie.genres
    ]

    reload(rows)
