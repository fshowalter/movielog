from movielog import watchlist
from movielog.cli import person_searcher, select_person


def prompt() -> None:
    person = select_person.prompt(person_searcher.search_directors_by_name)
    if person:
        watchlist.add_director(imdb_id=person.imdb_id, name=person.name)
