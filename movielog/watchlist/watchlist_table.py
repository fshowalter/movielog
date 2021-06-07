from __future__ import annotations

from typing import Optional, Sequence, TypedDict

from movielog import db

TABLE_NAME = "watchlist"

CREATE_DDL = """
  "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  "movie_imdb_id" TEXT NOT NULL
      REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
  "director_imdb_id" TEXT
      REFERENCES people(imdb_id) DEFERRABLE INITIALLY DEFERRED,
  "performer_imdb_id" TEXT
      REFERENCES people(imdb_id) DEFERRABLE INITIALLY DEFERRED,
  "writer_imdb_id" TEXT
      REFERENCES people(imdb_id) DEFERRABLE INITIALLY DEFERRED,
  "collection_name" TEXT,
  "slug" TEXT NOT NULL
"""

INSERT_DDL = """
  INSERT INTO {0}(
      movie_imdb_id,
      director_imdb_id,
      performer_imdb_id,
      writer_imdb_id,
      collection_name,
      slug)
  VALUES(
      :movie_imdb_id,
      :director_imdb_id,
      :performer_imdb_id,
      :writer_imdb_id,
      :collection_name,
      :slug);
"""


class Row(TypedDict):
    movie_imdb_id: str
    director_imdb_id: Optional[str]
    performer_imdb_id: Optional[str]
    writer_imdb_id: Optional[str]
    collection_name: Optional[str]
    slug: str


def reload(rows: Sequence[Row]) -> None:
    db.recreate_table(TABLE_NAME, CREATE_DDL)

    db.insert_into_table(
        table_name=TABLE_NAME,
        insert_ddl=INSERT_DDL.format(TABLE_NAME),
        rows=rows,
    )

    db.add_index(TABLE_NAME, "movie_imdb_id")
    db.add_index(TABLE_NAME, "director_imdb_id")
    db.add_index(TABLE_NAME, "performer_imdb_id")
    db.add_index(TABLE_NAME, "writer_imdb_id")

    db.validate_row_count(TABLE_NAME, len(rows))
