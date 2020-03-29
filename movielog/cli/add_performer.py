from prompt_toolkit.shortcuts import confirm

from movie_db import queries, watchlist
from movie_db.cli import _select_person


def prompt() -> None:
    person = _select_person.prompt('Performer', queries.search_performers_by_name)

    if person and confirm(f'Add {person.name}?'):
        watchlist.add_performer(person.imdb_id, person.name)
