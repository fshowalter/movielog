from __future__ import annotations

import json
from dataclasses import dataclass

from movielog.cli import query_formatter
from movielog.repository import api as repository_api


@dataclass
class SearchResult(object):
    imdb_id: str
    full_title: str
    principal_cast_names: list[str]


def search(title: str) -> list[SearchResult]:
    title_with_wildcards = query_formatter.add_wildcards(title)

    query = """
        SELECT imdb_id, full_title, principal_cast
        FROM titles WHERE title LIKE "{0}" ORDER BY title;
        """

    return [
        SearchResult(
            imdb_id=row["imdb_id"],
            full_title=row["full_title"],
            principal_cast_names=json.loads(row["principal_cast"]),
        )
        for row in repository_api.db.fetch_all(query.format(title_with_wildcards))
    ]
