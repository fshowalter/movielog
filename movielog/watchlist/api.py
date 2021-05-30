import copy
import operator

from slugify import slugify

from movielog.watchlist import collections as watchlist_collections
from movielog.watchlist import (
    directors,
    performers,
    person,
    serializer,
    watchlist_table,
    writers,
)
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


def add_director(imdb_id: str, name: str) -> Director:
    director = Director(
        frozen=False,
        name=name,
        imdb_id=imdb_id,
        slug=person.slug_for_name(name),
        movies=directors.movies_for_director(imdb_id, name),
    )
    serializer.serialize(director)

    return director


def add_performer(imdb_id: str, name: str) -> Performer:
    performer = Performer(
        frozen=False,
        name=name,
        imdb_id=imdb_id,
        slug=person.slug_for_name(name),
        movies=performers.movies_for_performer(imdb_id, name),
    )
    serializer.serialize(performer)

    return performer


def add_writer(imdb_id: str, name: str) -> Writer:
    writer = Writer(
        frozen=False,
        name=name,
        imdb_id=imdb_id,
        slug=person.slug_for_name(name),
        movies=writers.movies_for_writer(imdb_id, name),
    )
    serializer.serialize(writer)

    return writer


def add_movie_to_collection(
    collection: Collection, imdb_id: str, title: str, year: str
) -> Collection:
    collection_copy = copy.deepcopy(collection)

    collection_copy.movies.append(Movie(imdb_id=imdb_id, title=title, year=year))

    collection_copy.movies.sort(key=operator.attrgetter("year"))

    serializer.serialize(collection_copy)

    return collection_copy


def add_collection(name: str) -> Collection:
    slug = slugify(name, replacements=[("'", "")])

    collection = Collection(name=name, slug=slug, movies=[])

    serializer.serialize(collection)

    return collection


def refresh_credits() -> None:
    directors.refresh_movies()
    performers.refresh_movies()
    writers.refresh_movies()


def export_data() -> None:
    people: list[Person] = []
    people.extend(directors.deserialize_all())
    people.extend(performers.deserialize_all())
    people.extend(writers.deserialize_all())
    watchlist_table.update(people, collections())
    exports_api.export()
