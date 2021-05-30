from movielog import api as movielog_api
from movielog.cli import person_searcher, select_person


def prompt() -> None:
    person = select_person.prompt(person_searcher.search_writers_by_name)

    if person:
        movielog_api.add_writer(imdb_id=person.imdb_id, name=person.name)
