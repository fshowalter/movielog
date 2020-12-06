from typing import List, Sequence, Set

from movielog import watchlist_collection, watchlist_person, watchlist_table

Director = watchlist_person.Director
Performer = watchlist_person.Performer
Writer = watchlist_person.Writer
Collection = watchlist_collection.Collection
Movie = watchlist_table.Movie


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


def refresh_credits() -> None:
    watchlist_person.refresh_credits()


def load_all() -> List[Movie]:
    titles: List[Movie] = []

    for collection in watchlist_collection.all_items():
        titles.extend(watchlist_table.movies_for_collection(collection))

    for person in watchlist_person.all_items():
        titles.extend(watchlist_table.movies_for_person(person))

    return titles


def imdb_ids() -> Set[str]:
    return set([title.movie_imdb_id for title in load_all()])
