from typing import Sequence

from movielog import (
    imdb_data,
    watchlist_collection,
    watchlist_person,
    watchlist_titles_table,
)

Director = watchlist_person.Director
Performer = watchlist_person.Performer
Writer = watchlist_person.Writer
Collection = watchlist_collection.Collection


def add_director(imdb_id: str, name: str) -> Director:
    return watchlist_person.add(Director, imdb_id=imdb_id, name=name)


def add_performer(imdb_id: str, name: str) -> Performer:
    return watchlist_person.add(Performer, imdb_id=imdb_id, name=name)


def add_writer(imdb_id: str, name: str) -> Writer:
    return watchlist_person.add(Writer, imdb_id=imdb_id, name=name)


def all_collections() -> Sequence[Collection]:
    return watchlist_collection.all_items()


def add_collection(name: str) -> Collection:
    return watchlist_collection.add(name)


def update_watchlist_titles_table() -> None:
    watchlist_titles_table.update()
    imdb_data.update(watchlist_titles_table.imdb_ids())
