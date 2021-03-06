from movielog import watchlist
from movielog.cli import person_searcher, select_person


def prompt() -> None:
    person = select_person.prompt(person_searcher.search_performers_by_name)

    if person:
        watchlist.add_performer(imdb_id=person.imdb_id, name=person.name)
