from typing import Any, Dict, List

from movielog.internal import db


class Result(object):
    def __init__(self, row: Dict[str, str]) -> None:
        self.imdb_id: str = row["imdb_id"]
        self.title: str = row["title"]
        self.year: int = int(row["year"])
        self.directors: List[str] = []
        self.principals: List[str] = []


def search(query: str) -> List[Result]:
    with db.connect() as connection:
        search_results = _fetch_results(connection, query)
        _append_directors(connection, search_results)
        _append_principals(connection, search_results)

    return search_results


def _fetch_results(connection: db.Connection, query: str) -> List[Result]:
    cursor = connection.cursor()
    rows = cursor.execute(query).fetchall()

    search_results: List[Result] = []

    for row in rows:
        search_result = Result(row)
        search_results.append(search_result)

    return search_results


def _append_directors(connection: db.Connection, search_results: List[Result]) -> None:
    cursor = connection.cursor()
    rows = cursor.execute(
        """
        SELECT movies.imdb_id, full_name, sequence FROM movies INNER JOIN directing_credits
        ON movies.imdb_id = directing_credits.movie_imdb_id INNER JOIN people
        ON people.imdb_id = directing_credits.person_imdb_id
        WHERE movies.imdb_id IN ({0}) ORDER BY sequence;
        """.format(  # noqa: S608
            _format_title_ids(search_results)
        ),
    ).fetchall()

    results_hash = _hash_rows_by_title_id(rows)

    for search_result in search_results:
        search_result_directors = results_hash.get(search_result.imdb_id)
        if search_result_directors:
            search_result.directors.extend(
                list(dict.fromkeys(search_result_directors).keys())
            )


def _append_principals(connection: db.Connection, search_results: List[Result]) -> None:
    cursor = connection.cursor()
    rows = cursor.execute(
        """
        SELECT movies.imdb_id, full_name, sequence FROM movies INNER JOIN principals
        ON movies.imdb_id = principals.movie_imdb_id INNER JOIN people
        ON people.imdb_id = principals.person_imdb_id
        WHERE principals.category IN ('actor', 'actress') AND movies.imdb_id IN ({0})
        ORDER BY sequence;
        """.format(  # noqa: S608
            _format_title_ids(search_results)
        ),
    ).fetchall()

    results_hash = _hash_rows_by_title_id(rows)

    for search_result in search_results:
        search_result_principals = results_hash.get(search_result.imdb_id)

        if search_result_principals:
            search_result.principals.extend(
                list(dict.fromkeys(search_result_principals).keys())
            )


def _hash_rows_by_title_id(rows: List[Any]) -> Dict[str, List[str]]:
    results_hash: Dict[str, List[str]] = {}

    for row in rows:
        title_id = row["imdb_id"]
        if results_hash.get(title_id) is None:
            results_hash[title_id] = []
        results_hash[title_id].append(row["full_name"])

    return results_hash


def _format_title_ids(movies: List[Result]) -> str:
    return ",".join('"{0}"'.format(movie.imdb_id) for movie in movies)
