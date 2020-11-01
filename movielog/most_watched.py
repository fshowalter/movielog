import json
import os
from sqlite3 import Row
from typing import Dict, List, Sequence, Union

from movielog import db
from movielog.logger import logger

SLUG = "slug"


class Person(object):
    @classmethod
    def to_exclude_query_snippit(cls) -> str:
        ids_to_exclude = [
            "nm0498278",  # Stan Lee
            "nm0456158",  # Jack Kirby
            "nm4160687",  # Jim Starlin
            "nm0800209",  # Joe Simon
            "nm1293367",  # Larry Lieber
            "nm1921680",  # Steve Englehart
            "nm3238648",  # Steve Gan
            "nm2757098",  # Bill Mantlo
            "nm0317493",  # Keith Giffen
            "nm1411347",  # Don Heck
        ]

        exclude_strings = []

        for person_id in ids_to_exclude:
            exclude_strings.append('person_imdb_id != "{0}"'.format(person_id))

        return " AND ".join(exclude_strings)

    @classmethod
    def most_watched_query(cls, person_type: str) -> str:
        return """
        SELECT
            person_imdb_id
            , full_name
            , count({0}_credits.person_imdb_id) AS count
        FROM viewings
        LEFT JOIN {0}_credits ON {0}_credits.movie_imdb_id = viewings.movie_imdb_id
        LEFT JOIN people ON person_imdb_id = people.imdb_id
        WHERE
            {1}
            AND (notes IS NULL OR notes != "(uncredited)")
        GROUP BY
            (person_imdb_id)
        ORDER BY
            count DESC
        LIMIT 10;
        """.format(  # noqa: S608
            person_type, cls.to_exclude_query_snippit()
        )

    @classmethod
    def most_watched_for_years_query(cls, person_type: str) -> str:
        return """
            SELECT
                person_imdb_id
            , full_name
            , strftime('%Y', viewings.date) AS viewing_year
            , count({0}_credits.person_imdb_id) AS count
            FROM viewings
            LEFT JOIN {0}_credits ON {0}_credits.movie_imdb_id = viewings.movie_imdb_id
            LEFT JOIN people ON person_imdb_id = people.imdb_id
            WHERE
                {1}
                AND (
                notes IS NULL OR (
                    notes != "(uncredited)"
                    AND notes NOT LIKE  "%(characters)%"
                    AND notes NOT LIKE "%(characters - uncredited)%"
                )
                )
            GROUP BY
                viewing_year
            , person_imdb_id
            ORDER BY
                viewing_year
            , count DESC;
        """.format(  # noqa: S608
            person_type, cls.to_exclude_query_snippit()
        )

    @classmethod
    def build_reviewed_watchlist_cache(cls, person_type: str) -> Dict[str, str]:
        query = """
            SELECT DISTINCT
                ({0}_imdb_id) as person_imdb_id
            , watchlist_titles.slug
            FROM reviews
            LEFT JOIN watchlist_titles ON reviews.movie_imdb_id = watchlist_titles.movie_imdb_id
            LEFT JOIN people ON watchlist_titles.{0}_imdb_id = people.imdb_id
            WHERE {0}_imdb_id IS NOT NULL;
            """.format(  # noqa: S608
            person_type
        )

        rows = db.exec_query(query)
        cache: Dict[str, str] = {}

        for row in rows:
            cache[row["person_imdb_id"]] = row[SLUG]

        return cache


class Movie(object):
    @classmethod
    def most_watched_query(cls) -> str:
        return """
        SELECT
            count(viewings.movie_imdb_id) AS count
            , movies.title
            , movies.year
            , movies.imdb_id
            , slug
        FROM viewings
        INNER JOIN movies ON movies.imdb_id = viewings.movie_imdb_id
        LEFT JOIN reviews ON reviews.movie_imdb_id = movies.imdb_id
        GROUP BY
            viewings.movie_imdb_id
        ORDER BY
            count DESC
        LIMIT 10
        """

    @classmethod
    def most_watched_for_years_query(cls) -> str:
        return """
        SELECT
            count(viewings.movie_imdb_id) AS count
            , movies.title
            , movies.year
            , movies.imdb_id
            , slug
            , strftime('%Y', viewings.date) AS viewing_year
        FROM viewings
        INNER JOIN movies ON movies.imdb_id = viewings.movie_imdb_id
        LEFT JOIN reviews ON reviews.movie_imdb_id = movies.imdb_id
        GROUP BY
            viewing_year
            , viewings.movie_imdb_id
        ORDER BY
            viewing_year
            , count DESC
        """

    @classmethod
    def build_reviewed_cache(cls) -> Dict[str, str]:
        query = """
        SELECT DISTINCT
            movie_imdb_id as imdb_id
        , slug
        FROM reviews
        """

        rows = db.exec_query(query)
        cache: Dict[str, str] = {}

        for row in rows:
            cache[row["imdb_id"]] = row[SLUG]

        return cache


ListOfRows = List[Dict[str, str]]
RowsByYear = Dict[str, ListOfRows]
ListOfRowsByYear = List[Dict[str, Union[str, ListOfRows]]]


def write_file(
    rows: ListOfRowsByYear,
    filename: str,
) -> None:
    file_path = os.path.join("export", "{0}.json".format(filename))

    with open(file_path, "w") as output_file:
        output_file.write(json.dumps(rows))


def most_watched_by_year_rows_to_dict(
    rows: Sequence[Row], cache: Dict[str, str], cache_key: str
) -> RowsByYear:
    rows_by_year: RowsByYear = {}

    for row in rows:
        viewing_year = row["viewing_year"]
        viewing_year_rows = rows_by_year.get(viewing_year, [])
        row_as_dict = dict(row)
        row_as_dict[SLUG] = cache.get(row_as_dict[cache_key], None)
        row_as_dict.pop("viewing_year")
        viewing_year_rows.append(row_as_dict)
        rows_by_year[viewing_year] = viewing_year_rows

    return rows_by_year


def most_watched_rows_to_list(
    rows: Sequence[Row], cache: Dict[str, str], key: str
) -> ListOfRows:
    row_list = []

    for row in rows:
        row_as_dict = dict(row)
        row_as_dict[SLUG] = cache.get(row_as_dict[key], None)
        row_list.append(row_as_dict)

    return row_list


def most_watched_dict_to_list_of_dicts(
    rows_by_year: RowsByYear, key: str
) -> ListOfRowsByYear:
    list_of_rows_by_year: ListOfRowsByYear = []

    for year in rows_by_year.keys():
        list_of_rows_by_year.append({"year": year, key: rows_by_year[year][:10]})

    return list_of_rows_by_year


def build_most_watched_persons(
    cache_credit_type: str, watchlist_credit_type: str, output_file_name: str
) -> None:
    most_watched_by_year_rows = db.exec_query(
        Person.most_watched_for_years_query(watchlist_credit_type)
    )
    cache = Person.build_reviewed_watchlist_cache(cache_credit_type)

    rows_by_year = most_watched_by_year_rows_to_dict(
        most_watched_by_year_rows, cache, "person_imdb_id"
    )
    most_watched_rows = db.exec_query(Person.most_watched_query(watchlist_credit_type))
    rows_by_year["all"] = most_watched_rows_to_list(
        most_watched_rows, cache, "person_imdb_id"
    )

    list_of_rows_by_year = most_watched_dict_to_list_of_dicts(
        rows_by_year, "{0}s".format(cache_credit_type)
    )

    write_file(list_of_rows_by_year, output_file_name)


def build_most_watched_movies(output_file_name: str) -> None:
    most_watched_by_year_rows = db.exec_query(Movie.most_watched_for_years_query())

    cache = Movie.build_reviewed_cache()

    rows_by_year = most_watched_by_year_rows_to_dict(
        most_watched_by_year_rows, cache, "imdb_id"
    )
    most_watched_rows = db.exec_query(Movie.most_watched_query())
    rows_by_year["all"] = most_watched_rows_to_list(most_watched_rows, cache, "imdb_id")

    list_of_rows_by_year = most_watched_dict_to_list_of_dicts(rows_by_year, "movies")

    write_file(list_of_rows_by_year, output_file_name)


def log_heading(heading: str) -> None:
    logger.log("=== Begin exporting {}...", heading)


def export() -> None:
    log_heading("most watched directors")
    build_most_watched_persons("director", "directing", "mostWatchedDirectors")
    log_heading("most watched performers")
    build_most_watched_persons("performer", "performing", "mostWatchedPerformers")
    log_heading("most watched writers")
    build_most_watched_persons("writer", "writing", "mostWatchedWriters")
    log_heading("most watched movies")
    build_most_watched_movies("mostWatchedMovies")
