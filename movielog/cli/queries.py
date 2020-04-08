from typing import List

from movielog.cli import movie_searcher, person_searcher

PersonSearchResult = person_searcher.Result
MovieSearchResult = movie_searcher.Result


def search_directors_by_name(
    name_query: str, limit: int = 10
) -> List[PersonSearchResult]:
    query = _parse_query(name_query)

    full_query = """
        SELECT distinct(people.imdb_id), full_name, known_for_title_ids FROM people
        INNER JOIN directing_credits ON people.imdb_id = directing_credits.person_id
        WHERE full_name LIKE "{0}" ORDER BY full_name LIMIT {1};
        """.format(
        query, limit
    )  # noqa: S608

    return person_searcher.search(full_query)


def search_movies_by_title(title_query: str) -> List[MovieSearchResult]:
    query = _parse_query(title_query)

    full_query = """
        SELECT imdb_id, title, year FROM movies WHERE title LIKE "{0}" ORDER BY title;
        """.format(
        query
    )  # noqa: S608
    return movie_searcher.search(full_query)


def search_performers_by_name(
    name_query: str, limit: int = 10
) -> List[PersonSearchResult]:
    query = _parse_query(name_query)

    full_query = """
        SELECT distinct(people.imdb_id), full_name, known_for_title_ids FROM people
        WHERE full_name LIKE "{0}" ORDER BY full_name LIMIT {1};
        """.format(
        query, limit
    )  # noqa: S608

    return person_searcher.search(full_query)


def search_writers_by_name(
    name_query: str, limit: int = 10
) -> List[PersonSearchResult]:
    query = _parse_query(name_query)

    full_query = """
        SELECT distinct(people.imdb_id), full_name, known_for_title_ids FROM people
        INNER JOIN writing_credits ON people.imdb_id = writing_credits.person_id
        WHERE full_name LIKE "{0}" ORDER BY full_name LIMIT {1};
        """.format(
        query, limit
    )  # noqa: S608

    return person_searcher.search(full_query)


def _parse_query(query: str) -> str:
    start_wildcard = "%"
    end_wildcard = "%"

    if query.startswith("^"):
        query = query[1:]
        start_wildcard = ""
    if query.endswith("$"):
        query = query[:-1]
        end_wildcard = ""

    return f"{start_wildcard}{query}{end_wildcard}"
