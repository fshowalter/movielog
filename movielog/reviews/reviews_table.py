from datetime import date
from typing import Protocol, Sequence, TypedDict

from movielog import db

TABLE_NAME = "reviews"

CREATE_DDL = """
  "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  "movie_imdb_id" TEXT NOT NULL REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
  "date" DATE NOT NULL,
  "sequence" INT NOT NULL,
  "grade" TEXT NOT NULL,
  "grade_value" INT NOT NULL,
  "slug" TEXT NOT NULL,
  "venue" TEXT NOT NULL
"""

INSERT_DDL = """
  INSERT INTO {0}(movie_imdb_id, date, sequence, grade, grade_value, slug, venue)
    VALUES(:movie_imdb_id, :date, :sequence, :grade, :grade_value, :slug, :venue);
"""


class Row(TypedDict):
    movie_imdb_id: str
    date: date
    sequence: int
    grade: str
    grade_value: float
    slug: str
    venue: str


class Review(Protocol):
    sequence: int
    imdb_id: str
    date: date
    grade: str
    venue: str
    slug: str

    @property
    def grade_value(self) -> float:
        """MyPy needs this to recognize the prop."""


def reload(rows: Sequence[Row]) -> None:
    db.recreate_table(TABLE_NAME, CREATE_DDL)

    db.insert_into_table(
        table_name=TABLE_NAME,
        insert_ddl=INSERT_DDL.format(TABLE_NAME),
        rows=rows,
    )

    db.add_index(TABLE_NAME, "movie_imdb_id")

    db.validate_row_count(TABLE_NAME, len(rows))


def update(reviews: Sequence[Review]) -> None:
    reload(
        [
            Row(
                movie_imdb_id=review.imdb_id,
                date=review.date,
                sequence=review.sequence,
                grade=review.grade,
                grade_value=review.grade_value,
                slug=review.slug,
                venue=review.venue,
            )
            for review in reviews
        ]
    )
