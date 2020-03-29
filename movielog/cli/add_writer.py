from prompt_toolkit.shortcuts import confirm

from movielog import queries, watchlist
from movielog.cli.internal import select_person


def prompt() -> None:
    person = select_person.prompt("Writer", queries.search_writers_by_name)

    if person and confirm(f"Add {person.name}?"):
        watchlist.add_writer(person.imdb_id, person.name)
