import json
import math
import os
import statistics
from dataclasses import asdict, dataclass
from sqlite3 import Row
from typing import Sequence

from movielog import db

viewings_by_release_year_query = """
    SELECT
      movies.year
    , COUNT(DISTINCT movie_imdb_id) AS viewings
    FROM viewings
    LEFT JOIN movies ON movie_imdb_id = movies.imdb_id
    GROUP BY
      (movies.year)
"""


ratings_by_release_year_query = """
    SELECT DISTINCT
        (movies.imdb_id)
      , movies.year
      , avg(grade_value) as rating
    FROM reviews
    LEFT JOIN movies ON movies.imdb_id = reviews.movie_imdb_id
    GROUP BY
        year
  """

watchlist_collections_progress_query = """
    SELECT
        a.collection_name AS name
      , total
      , reviewed
    FROM (
          SELECT
              collection_name
            , count(reviews.movie_imdb_id) AS reviewed
          FROM watchlist_titles
          LEFT JOIN reviews ON reviews.movie_imdb_id = watchlist_titles.movie_imdb_id
          WHERE collection_name IS NOT NULL
          GROUP BY
              collection_name
        ) AS A
    LEFT JOIN (
                SELECT
                    count(movie_imdb_id) AS total
                  , collection_name
                FROM watchlist_titles
                WHERE collection_name IS NOT NULL
                GROUP BY
                    collection_name
              ) AS B ON a.collection_name = b.collection_name
  """


def watchlist_progress_query(watchlist_type: str) -> str:
    return """
    SELECT
        {0}_imdb_id AS imdb_id
      , full_name AS name
      , total
      , reviewed
    FROM (
          SELECT
              a.{0}_imdb_id
            , total
            , reviewed
          FROM (
                  SELECT
                      {0}_imdb_id
                    , count(reviews.movie_imdb_id) AS reviewed
                  FROM watchlist_titles
                  LEFT JOIN reviews ON reviews.movie_imdb_id = watchlist_titles.movie_imdb_id
                  WHERE {0}_imdb_id IS NOT NULL
                  GROUP BY
                      {0}_imdb_id
                ) AS A
          LEFT JOIN (
                      SELECT
                          count(movie_imdb_id) AS total
                        , {0}_imdb_id
                      FROM watchlist_titles
                      WHERE {0}_imdb_id IS NOT NULL
                      GROUP BY
                          {0}_imdb_id
                    ) AS B ON a.{0}_imdb_id = b.{0}_imdb_id)
    INNER JOIN people ON {0}_imdb_id = people.imdb_id
    ORDER BY
        full_name;
    """.format(  # noqa: S608
        watchlist_type
    )


def most_watched_query(person_type: str) -> str:
    return """
      SELECT
          full_name
        , count({0}_credits.person_imdb_id) AS count
      FROM viewings
      LEFT JOIN {0}_credits ON {0}_credits.movie_imdb_id = viewings.movie_imdb_id
      LEFT JOIN people ON person_imdb_id = people.imdb_id
      WHERE notes IS NULL
        OR notes != "(uncredited)"
      GROUP BY
          (person_imdb_id)
      ORDER BY
          count DESC
      LIMIT 10;
    """.format(  # noqa: S608
        person_type
    )


def write_results(rows: Sequence[Row], filename: str,) -> None:
    file_path = os.path.join("export", "{0}.json".format(filename))

    with open(file_path, "w") as output_file:
        output_file.write(json.dumps([dict(row) for row in rows]))


def weighted_average(numbers: Sequence[int]) -> float:
    number_of_items = len(numbers)
    average = statistics.mean(numbers)
    quantity = 3
    reducer = 0.5

    return (reducer * average) + 5 * (1 - reducer) * (  # no-qa: WPS221
        1 - ((math.e) ** (-number_of_items / quantity))
    )


@dataclass
class HighestRated(object):
    full_name: str
    rating: float

    @classmethod
    def query(cls, credit_type: str) -> str:
        return """
            SELECT
                full_name, GROUP_CONCAT(reviews.grade_value) as ratings,
              count(reviews.sequence) as count
            FROM reviews
            LEFT JOIN {0}_credits ON {0}_credits.movie_imdb_id = reviews.movie_imdb_id
            LEFT JOIN people ON person_imdb_id = people.imdb_id
            WHERE notes IS NULL
              OR notes != "(uncredited)"
            GROUP BY
                (person_imdb_id);
        """.format(  # noqa: S608
            credit_type
        )

    @classmethod
    def compute(cls, credit_type: str, filename: str) -> None:
        hightest_rated = []

        for row in db.exec_query(cls.query(credit_type)):
            ratings = [int(rating) for rating in row["ratings"].split(",")]
            hightest_rated.append(
                cls(full_name=row["full_name"], rating=weighted_average(ratings),)
            )

        hightest_rated.sort(key=lambda rated: rated.rating, reverse=True)

        file_path = os.path.join("export", "{0}.json".format(filename))

        with open(file_path, "w") as output_file:
            output_file.write(
                json.dumps(list(asdict(rated) for rated in hightest_rated[:10]))
            )


def by_release_year() -> None:
    write_results(
        db.exec_query(viewings_by_release_year_query), "viewingsByReleaseYear"
    )

    write_results(db.exec_query(ratings_by_release_year_query), "ratingsByReleaseYear")


def watchlist_progress() -> None:
    write_results(
        db.exec_query(watchlist_progress_query("director")), "directorWatchlistProgress"
    )

    write_results(
        db.exec_query(watchlist_progress_query("performer")),
        "performerWatchlistProgress",
    )

    write_results(
        db.exec_query(watchlist_progress_query("writer")), "writerWatchlistProgress"
    )

    write_results(
        db.exec_query(watchlist_collections_progress_query),
        "watchlistCollectionsProgress",
    )


def most_watched() -> None:
    write_results(
        db.exec_query(most_watched_query("directing")), "mostWatchedDirectors",
    )

    write_results(
        db.exec_query(most_watched_query("performing")), "mostWatchedPerformers",
    )

    write_results(
        db.exec_query(most_watched_query("writing")), "mostWatchedWriters",
    )


def hightest_rated() -> None:
    HighestRated.compute("performing", "highestRatedPerformers")
    HighestRated.compute("directing", "highestRatedDirectors")
    HighestRated.compute("writing", "highestRatedWriters")


def export() -> None:
    by_release_year()
    watchlist_progress()
    most_watched()
    hightest_rated()
