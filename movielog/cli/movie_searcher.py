from dataclasses import dataclass
from typing import Dict, List

from movielog import db
from movielog.cli import query_formatter


@dataclass
class Result(object):
    __slots__ = (
        "imdb_id",
        "title",
        "year",
        "principal_cast_ids",
        "principal_cast_names",
    )
    imdb_id: str
    title: str
    year: int
    principal_cast_ids: str
    principal_cast_names: List[str]

    @classmethod
    def from_query_result(cls, row: Dict[str, str]) -> "Result":
        return cls(
            imdb_id=row["imdb_id"],
            title=row["title"],
            year=int(row["year"]),
            principal_cast_ids=row["principal_cast_ids"],
            principal_cast_names=[],
        )


def search_by_title(title: str) -> List[Result]:
    title_with_wildcards = query_formatter.add_wildcards(title)

    query = """
        SELECT imdb_id, title, year, principal_cast_ids
        FROM movies WHERE title LIKE "{0}" ORDER BY title;
        """.format(  # noqa: S608
        title_with_wildcards
    )

    with db.connect() as connection:
        search_results = fetch_results(connection, query)
        resolve_principals(connection, search_results)

    return search_results


def fetch_results(connection: db.Connection, query: str) -> List[Result]:
    cursor = connection.cursor()
    rows = cursor.execute(query).fetchall()

    search_results: List[Result] = []

    for row in rows:
        search_result = Result.from_query_result(row)
        search_results.append(search_result)

    return search_results


def resolve_principals(connection: db.Connection, search_results: List[Result]) -> None:
    name_cache = build_name_cache(connection=connection, search_results=search_results)

    for search_result in search_results:
        for principal_id in search_result.principal_cast_ids.split(","):
            search_result.principal_cast_names.append(name_cache[principal_id])


def build_name_cache(
    connection: db.Connection, search_results: List[Result]
) -> Dict[str, str]:
    cursor = connection.cursor()

    rows = cursor.execute(
        """
        SELECT imdb_id, full_name FROM people where imdb_id IN ({0});
        """.format(  # noqa: S608
            format_principal_cast_ids(search_results)
        ),
    ).fetchall()

    return {row["imdb_id"]: row["full_name"] for row in rows}


def format_principal_cast_ids(search_results: List[Result]) -> str:
    cast_ids: List[str] = []

    for search_result in search_results:
        cast_ids.extend(search_result.principal_cast_ids.split(","))

    return ",".join('"{0}"'.format(cast_id) for cast_id in cast_ids)
