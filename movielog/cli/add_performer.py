from movielog.cli import person_searcher, select_person
from movielog.repository import api as repository_api


def prompt() -> None:
    person = select_person.prompt(person_searcher.search_by_name)

    if person:
        repository_api.add_person_to_watchlist(
            watchlist="performers", imdb_id=person.imdb_id, name=person.name
        )
