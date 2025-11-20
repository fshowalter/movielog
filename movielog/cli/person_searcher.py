from dataclasses import dataclass

from movielog.repository import imdb_http_person


@dataclass
class SearchResult:
    imdb_id: str
    name: str
    known_for_titles: list[str]


def search_by_name(imdb_id: str) -> list[SearchResult]:
    person_page = imdb_http_person.get_person_page(imdb_id)

    return [
        SearchResult(
            imdb_id=imdb_id,
            name=person_page.name,
            known_for_titles=person_page.known_for_titles,
        )
    ]
