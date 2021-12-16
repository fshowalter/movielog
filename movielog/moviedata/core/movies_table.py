from functools import lru_cache
from typing import Optional, Sequence, Set, TypedDict

from movielog import db

TABLE_NAME = "movies"

CREATE_DDL = """
  "imdb_id" TEXT PRIMARY KEY NOT NULL,
  "title" TEXT NOT NULL,
  "original_title" TEXT,
  "year" INT NOT NULL,
  "runtime_minutes" INT,
  "principal_cast_ids" TEXT,
  "votes" INT,
  "imdb_rating" FLOAT
"""

INSERT_DDL = """
  INSERT INTO {0}(
      imdb_id
    , title
    , original_title
    , year
    , runtime_minutes
    , principal_cast_ids
    , votes
    , imdb_rating
    )
    VALUES(
      :imdb_id
    , :title
    , :original_title
    , :year
    , :runtime_minutes
    , :principal_cast_ids
    , :votes
    , :imdb_rating
    )
"""


class Row(TypedDict):
    imdb_id: str
    title: str
    original_title: Optional[str]
    year: int
    runtime_minutes: Optional[int]
    principal_cast_ids: Optional[str]
    votes: Optional[int]
    imdb_rating: Optional[float]


def reload(rows: Sequence[Row]) -> None:
    db.recreate_table(TABLE_NAME, CREATE_DDL)

    db.insert_into_table(
        table_name=TABLE_NAME,
        insert_ddl=INSERT_DDL.format(TABLE_NAME),
        rows=rows,
    )

    db.add_index(TABLE_NAME, "title")

    db.validate_row_count(TABLE_NAME, len(rows))

    movie_ids.cache_clear()


@lru_cache(1)
def movie_ids() -> Set[str]:
    return set(db.fetch_all("select imdb_id from movies", lambda cursor, row: row[0]))
