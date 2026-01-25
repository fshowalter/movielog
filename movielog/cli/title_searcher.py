from __future__ import annotations

from dataclasses import dataclass

from movielog.repository import api as repository_api


@dataclass
class SearchResult:
    imdb_id: str
    full_title: str
    principal_cast_names: list[str]


def search(token: str, title_id: str) -> list[SearchResult]:
    title_page = repository_api.get_title_page(token, title_id)

    return [
        SearchResult(
            imdb_id=title_id,
            full_title=f"{title_page.title} ({title_page.year})",
            principal_cast_names=title_page.principal_cast,
        )
    ]
