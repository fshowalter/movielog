from dataclasses import dataclass

from movielog.cli import query_formatter
from movielog.repository.db import db


@dataclass
class SearchResult(object):
    imdb_id: str
    name: str
    known_for_titles: list[str]


def search_by_name(name: str, limit: int = 10) -> list[SearchResult]:
    query = query_formatter.add_wildcards(name)

    full_query = """
        SELECT distinct imdb_id, full_name, known_for_titles FROM names
        WHERE full_name LIKE "{0}" ORDER BY full_name LIMIT {1};
    """

    return execute_search(full_query.format(query, limit))


def execute_search(query: str) -> list[SearchResult]:
    return [
        SearchResult(
            imdb_id=row["imdb_id"],
            name=row["full_name"],
            known_for_titles=row["known_for_titles"],
        )
        for row in db.fetch_all(query)
    ]
