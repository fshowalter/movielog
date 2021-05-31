from __future__ import annotations

from typing import Callable, Optional, Sequence, TypedDict

from movielog import db
from movielog.watchlist.collections import Collection
from movielog.watchlist.directors import Director
from movielog.watchlist.movies import Movie
from movielog.watchlist.performers import Performer
from movielog.watchlist.person import Person
from movielog.watchlist.writers import Writer

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


_row_builder: dict[type[Person], Callable[[Person, Movie], Row]] = {
    Director: lambda person, movie: Row(
        movie_imdb_id=movie.imdb_id,
        director_imdb_id=person.imdb_id,
        slug=person.slug,
        performer_imdb_id=None,
        writer_imdb_id=None,
        collection_name=None,
    ),
    Performer: lambda person, movie: Row(
        movie_imdb_id=movie.imdb_id,
        performer_imdb_id=person.imdb_id,
        slug=person.slug,
        director_imdb_id=None,
        writer_imdb_id=None,
        collection_name=None,
    ),
    Writer: lambda person, movie: Row(
        movie_imdb_id=movie.imdb_id,
        writer_imdb_id=person.imdb_id,
        slug=person.slug,
        performer_imdb_id=None,
        director_imdb_id=None,
        collection_name=None,
    ),
}


def update(
    watchlist_people: Sequence[Person], watchlist_collections: Sequence[Collection]
) -> None:
    rows: list[Row] = []

    for watchlist_person in watchlist_people:
        for person_movie in watchlist_person.movies:
            rows.append(
                _row_builder[type(watchlist_person)](watchlist_person, person_movie)
            )

    for collection in watchlist_collections:
        for collection_movie in collection.movies:
            rows.append(
                Row(
                    movie_imdb_id=collection_movie.imdb_id,
                    collection_name=collection.name,
                    slug=collection.slug,
                    performer_imdb_id=None,
                    writer_imdb_id=None,
                    director_imdb_id=None,
                )
            )

    reload(rows)
