from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Sequence, TypedDict

from movielog import db

if TYPE_CHECKING:
    from movielog.moviedata.extended.movies import Movie

TABLE_NAME = "writing_credits"

CREATE_DDL = """
  "movie_imdb_id" varchar(255) NOT NULL
      REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
  "person_imdb_id" varchar(255) NOT NULL
      REFERENCES people(imdb_id) DEFERRABLE INITIALLY DEFERRED,
  "group_id" INT NOT NULL,
  "sequence" INT NOT NULL,
  "notes" TEXT,
  PRIMARY KEY (movie_imdb_id, person_imdb_id, group_id, notes)
"""

INSERT_DDL = """
  INSERT INTO {0} (movie_imdb_id, person_imdb_id, group_id, sequence, notes)
      VALUES(:movie_imdb_id, :person_imdb_id, :group_id, :sequence, :notes);
"""


class Row(TypedDict):
    movie_imdb_id: str
    person_imdb_id: str
    group_id: int
    sequence: int
    notes: Optional[str]


def reload(rows: Sequence[Row]) -> None:
    db.recreate_table(TABLE_NAME, CREATE_DDL)

    db.insert_into_table(
        table_name=TABLE_NAME,
        insert_ddl=INSERT_DDL.format(TABLE_NAME),
        rows=rows,
    )

    db.add_index(TABLE_NAME, "person_imdb_id")

    db.validate_row_count(TABLE_NAME, len(rows))


def update(movies: list[Movie]) -> None:
    rows = [
        Row(
            movie_imdb_id=movie.imdb_id,
            person_imdb_id=writer.person_imdb_id,
            group_id=writer.group,
            sequence=writer.sequence,
            notes=writer.notes,
        )
        for movie in movies
        for writer in movie.writers
    ]

    reload(rows)
