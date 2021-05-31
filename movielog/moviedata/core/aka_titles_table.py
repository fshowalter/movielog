from typing import Optional, Sequence, TypedDict

from movielog import db

TABLE_NAME = "aka_titles"

CREATE_DDL = """
  "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  "movie_imdb_id" TEXT NOT NULL
      REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
  "sequence" INT NOT NULL,
  "title" TEXT NOT NULL,
  "region" TEXT,
  "language" TEXT,
  "types" TEXT,
  "attributes" TEXT,
  "is_original_title" BOOLEAN DEFAULT FALSE
"""

INSERT_DDL = """
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
      :is_original_title);
"""


class Row(TypedDict):
    movie_imdb_id: str
    sequence: int
    title: str
    region: Optional[str]
    language: Optional[str]
    types: Optional[str]
    attributes: Optional[str]
    is_original_title: bool


def reload(rows: Sequence[Row]) -> None:
    db.recreate_table(TABLE_NAME, CREATE_DDL)

    db.insert_into_table(
        table_name=TABLE_NAME,
        insert_ddl=INSERT_DDL.format(TABLE_NAME),
        rows=rows,
    )

    db.add_index(TABLE_NAME, "movie_imdb_id")
    db.add_index(TABLE_NAME, "region")
    db.add_index(TABLE_NAME, "title")

    db.validate_row_count(TABLE_NAME, len(rows))
