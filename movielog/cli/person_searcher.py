from dataclasses import dataclass

from movielog.repository import api as repository_api


@dataclass
class SearchResult:
    imdb_id: str
    name: str
    known_for_titles: list[str]


def search_by_name(imdb_id: str) -> list[SearchResult]:
    person_page = repository_api.get_person_page(imdb_id)

    return [
        SearchResult(
            imdb_id=imdb_id,
            name=person_page.name,
            known_for_titles=person_page.known_for_titles,
        )
    ]
