import json
from typing import Optional, TypedDict

from movielog.repository.datasets.dataset_title import DatasetTitle
from movielog.repository.db import db

TABLE_NAME = "titles"

CREATE_DDL = """
  "imdb_id" TEXT PRIMARY KEY NOT NULL,
  "title" TEXT NOT NULL,
  "original_title" TEXT,
  "full_title" TEXT NOT NULL,
  "year" INT NOT NULL,
  "runtime_minutes" INT,
  "principal_cast" JSON,
  "aka_titles" JSON,
  "imdb_votes" INT,
  "imdb_rating" FLOAT
"""

INSERT_DDL = """
  INSERT INTO {0}(
      imdb_id
    , title
    , original_title
    , full_title
    , year
    , runtime_minutes
    , principal_cast
    , imdb_votes
    , imdb_rating
    , aka_titles
    )
    VALUES(
      :imdb_id
    , :title
    , :original_title
    , :full_title
    , :year
    , :runtime_minutes
    , :principal_cast
    , :imdb_votes
    , :imdb_rating
    , :aka_titles
    )
"""


class Row(TypedDict):
    imdb_id: str
    title: str
    original_title: str
    year: int
    full_title: str
    runtime_minutes: Optional[int]
    principal_cast: str
    aka_titles: str
    imdb_votes: Optional[int]
    imdb_rating: Optional[float]


def reload(titles: list[DatasetTitle]) -> None:
    db.recreate_table(TABLE_NAME, CREATE_DDL)

    db.insert_into_table(
        table_name=TABLE_NAME,
        insert_ddl=INSERT_DDL.format(TABLE_NAME),
        rows=[
            Row(
                imdb_id=title["imdb_id"],
                title=title["title"],
                original_title=title["original_title"],
                year=title["year"],
                full_title=title["full_title"],
                runtime_minutes=title["runtime_minutes"],
                principal_cast=json.dumps(title["principal_cast"]),
                aka_titles=json.dumps(title["aka_titles"]),
                imdb_rating=title["imdb_rating"],
                imdb_votes=title["imdb_votes"],
            )
            for title in titles
        ],
    )

    db.add_index(TABLE_NAME, "title")

    db.validate_row_count(TABLE_NAME, len(titles))
