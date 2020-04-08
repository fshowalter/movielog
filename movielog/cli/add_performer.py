from prompt_toolkit.shortcuts import confirm

from movielog import watchlist_person
from movielog.cli import select_person, queries


def prompt() -> None:
    person = select_person.prompt("Performer", queries.search_performers_by_name)

    if person and confirm(f"Add {person.name}?"):
        watchlist_person.add(watchlist_person.Performer, person.imdb_id, person.name)
