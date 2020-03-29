from prompt_toolkit.shortcuts import confirm

from movielog import queries, watchlist
from movielog.cli.internal import select_person


def prompt() -> None:
    person = select_person.prompt("Performer", queries.search_performers_by_name)

    if person and confirm(f"Add {person.name}?"):
        watchlist.add_performer(person.imdb_id, person.name)
