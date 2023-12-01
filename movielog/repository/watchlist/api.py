from __future__ import annotations

from movielog.watchlist import collections as watchlist_collections
from movielog.watchlist import directors, performers, person, watchlist_table, writers
from movielog.watchlist.exports import api as exports_api

Collection = watchlist_collections.Collection
Director = directors.Director
Performer = performers.Performer
Writer = writers.Writer
Person = person.Person

collections = watchlist_collections.deserialize_all


add_director = directors.add

add_performer = performers.add

add_writer = writers.add

add_movie_to_collection = watchlist_collections.add_movie

add_collection = watchlist_collections.add


def refresh_credits() -> None:
    directors.refresh_movies()
    performers.refresh_movies()
    writers.refresh_movies()
    # watchlist_collections.update()


def export_data() -> None:
    people: list[Person] = []
    people.extend(directors.deserialize_all())
    people.extend(performers.deserialize_all())
    people.extend(writers.deserialize_all())
    watchlist_table.update(people, collections())
    exports_api.export()
