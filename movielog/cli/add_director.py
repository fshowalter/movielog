from prompt_toolkit.shortcuts import confirm

from movielog import queries, watchlist
from movielog.cli.controls import select_person


def prompt() -> None:
    person = select_person.prompt("Director", queries.search_directors_by_name)

    if person and confirm(f"Add {person.name}?"):
        watchlist.add_director(person.imdb_id, person.name)
