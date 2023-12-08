from movielog.cli import select_person
from movielog.repository import api as repository_api


def prompt() -> None:
    person = select_person.prompt()
    if person:
        repository_api.add_person_to_watchlist(
            watchlist="directors", imdb_id=person.imdb_id, name=person.name
        )
