from __future__ import annotations

from movielog.watchlist import collections as watchlist_collections
from movielog.watchlist import directors, performers, person, table_updater, writers
from movielog.watchlist.exports import api as exports_api
from movielog.watchlist.movies import Movie

Collection = watchlist_collections.Collection
Director = directors.Director
Performer = performers.Performer
Writer = writers.Writer
Person = person.Person

collections = watchlist_collections.deserialize_all


def movies() -> list[Movie]:
    people: list[Person] = []
    people.extend(directors.deserialize_all())
    people.extend(performers.deserialize_all())
    people.extend(writers.deserialize_all())

    all_movies = []

    for watchlist_person in people:
        all_movies.extend(watchlist_person.movies)

    for collection in collections():
        all_movies.extend(collection.movies)

    return all_movies


add_director = directors.add

add_performer = performers.add

add_writer = writers.add

add_movie_to_collection = watchlist_collections.add_movie

add_collection = watchlist_collections.add


def refresh_credits() -> None:
    directors.refresh_movies()
    performers.refresh_movies()
    writers.refresh_movies()


def export_data() -> None:
    people: list[Person] = []
    people.extend(directors.deserialize_all())
    people.extend(performers.deserialize_all())
    people.extend(writers.deserialize_all())
    table_updater.update(people, collections())
    exports_api.export()
