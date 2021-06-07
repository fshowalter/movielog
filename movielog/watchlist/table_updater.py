from __future__ import annotations

from typing import Callable, Sequence

from movielog.watchlist import watchlist_table
from movielog.watchlist.collections import Collection
from movielog.watchlist.directors import Director
from movielog.watchlist.movies import Movie
from movielog.watchlist.performers import Performer
from movielog.watchlist.person import Person
from movielog.watchlist.writers import Writer

_row_builder: dict[type[Person], Callable[[Person, Movie], watchlist_table.Row]] = {
    Director: lambda person, movie: watchlist_table.Row(
        movie_imdb_id=movie.imdb_id,
        director_imdb_id=person.imdb_id,
        slug=person.slug,
        performer_imdb_id=None,
        writer_imdb_id=None,
        collection_name=None,
    ),
    Performer: lambda person, movie: watchlist_table.Row(
        movie_imdb_id=movie.imdb_id,
        performer_imdb_id=person.imdb_id,
        slug=person.slug,
        director_imdb_id=None,
        writer_imdb_id=None,
        collection_name=None,
    ),
    Writer: lambda person, movie: watchlist_table.Row(
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
    rows: list[watchlist_table.Row] = []

    for watchlist_person in watchlist_people:
        for person_movie in watchlist_person.movies:
            rows.append(
                _row_builder[type(watchlist_person)](watchlist_person, person_movie)
            )

    for collection in watchlist_collections:
        for collection_movie in collection.movies:
            rows.append(
                watchlist_table.Row(
                    movie_imdb_id=collection_movie.imdb_id,
                    collection_name=collection.name,
                    slug=collection.slug,
                    performer_imdb_id=None,
                    writer_imdb_id=None,
                    director_imdb_id=None,
                )
            )

    watchlist_table.reload(rows)
