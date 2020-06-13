import json
import os
from sqlite3 import Row
from typing import Sequence

from movielog import db
from movielog.logger import logger

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


def write_results(rows: Sequence[Row], filename: str) -> None:
    file_path = os.path.join("export", "{0}.json".format(filename))

    with open(file_path, "w") as output_file:
        output_file.write(json.dumps([dict(row) for row in rows]))


def export() -> None:
    logger.log("==== Begin exporting {}...", "stats")
    viewings_by_release_year = db.exec_query(viewings_by_release_year_query)
    write_results(viewings_by_release_year, "viewingsByReleaseYear")

    ratings_by_release_year = db.exec_query(ratings_by_release_year_query)
    write_results(ratings_by_release_year, "ratingsByReleaseYear")

    director_watchlist_progress = db.exec_query(watchlist_progress_query("director"))
    write_results(director_watchlist_progress, "directorWatchlistProgress")

    performer_watchlist_progress = db.exec_query(watchlist_progress_query("performer"))
    write_results(performer_watchlist_progress, "performerWatchlistProgress")

    writer_watchlist_progress = db.exec_query(watchlist_progress_query("writer"))
    write_results(writer_watchlist_progress, "writerWatchlistProgress")

    watchlist_collections_progress = db.exec_query(watchlist_collections_progress_query)
    write_results(watchlist_collections_progress, "watchlistCollectionsProgress")
