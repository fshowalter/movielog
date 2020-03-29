from typing import Any, Dict, List, Set, Tuple

from movielog.internal import db


class Result(object):
    def __init__(self, row: Dict[str, str]) -> None:
        self.imdb_id = row["imdb_id"]
        self.name = row["full_name"]

        known_for_title_ids: List[str] = []
        if row["known_for_title_ids"]:
            known_for_title_ids = row["known_for_title_ids"].split(",")

        self.known_for_title_ids = known_for_title_ids
        self.known_for_titles: Set[str] = set()


def search(query: str) -> List[Result]:
    with db.connect() as connection:
        search_results, title_ids = _fetch_results(connection, query)
        titles = _resolve_known_for_title_ids(connection, title_ids)
        _expand_known_for_title_ids(search_results, titles)

    return search_results


def _expand_known_for_title_ids(
    search_results: List[Result], titles: Dict[str, str],
) -> None:
    for search_result in search_results:
        for title_id in search_result.known_for_title_ids:
            title = titles.get(title_id)
            if title is not None:
                search_result.known_for_titles.add(title)


def _fetch_results(
    connection: db.Connection, query: str,
) -> Tuple[List[Result], Set[str]]:  # noqa: WPS221
    cursor = connection.cursor()
    rows = cursor.execute(query).fetchall()

    return _parse_rows(rows)


def _parse_rows(rows: List[Any]) -> Tuple[List[Result], Set[str]]:
    search_results: List[Result] = []
    title_ids: Set[str] = set()

    for row in rows:
        search_result = Result(row)
        search_results.append(search_result)
        title_ids.update(search_result.known_for_title_ids)

    return (search_results, title_ids)


def _resolve_known_for_title_ids(
    connection: db.Connection, title_ids: Set[str]
) -> Dict[str, str]:
    cursor = connection.cursor()
    movie_results = cursor.execute(
        """
        SELECT id, title FROM movies
        WHERE id IN ({0});
        """.format(  # noqa: S608
            _format_title_ids(title_ids)
        ),
    ).fetchall()

    movies: Dict[str, str] = {}

    for row in movie_results:
        movies[row["id"]] = row["title"]

    return movies


def _format_title_ids(title_ids: Set[str]) -> str:
    return ",".join('"{0}"'.format(title_id) for title_id in title_ids)
