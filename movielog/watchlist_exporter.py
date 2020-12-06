import json
import os
from dataclasses import asdict, dataclass
from typing import Dict, List, Sequence

from movielog import db, watchlist, watchlist_table
from movielog.logger import logger

SLUG = "slug"
DIRECTOR_IMDB_ID = "director_imdb_id"
ETHAN_COEN_IMDB_ID = "nm0001053"
IMDB_ID = "imdb_id"


@dataclass
class WatchlistPersonExport(object):
    imdb_id: str
    name: str
    slug: str


@dataclass
class WatchlistPersonStatsExport(WatchlistPersonExport):
    title_count: int
    review_count: int


@dataclass
class WatchlistCollectionExport(object):
    name: str
    slug: str


@dataclass
class WatchlistCollectionStatsExport(WatchlistCollectionExport):
    title_count: int
    review_count: int


@dataclass
class WatchlistTitleExport(object):
    imdb_id: str
    title: str
    year: str
    sort_title: str
    release_date: str
    directors: List[WatchlistPersonExport]
    performers: List[WatchlistPersonExport]
    writers: List[WatchlistPersonExport]
    collections: List[WatchlistCollectionExport]


def export(watchlist_movies: Sequence[watchlist.Movie]) -> None:
    watchlist_table.update(watchlist_movies)

    MoviesExporter.export()
    PersonStatsExporter.export("director")
    PersonStatsExporter.export("performer")
    PersonStatsExporter.export("writer")
    CollectionStatsExporter.export()


class CollectionStatsExporter(object):
    @classmethod
    def write_file(cls, stats: List[WatchlistCollectionStatsExport]) -> None:
        file_path = os.path.join("export", "watchlist_collections.json")

        with open(file_path, "w") as output_file:
            output_file.write(json.dumps([asdict(stat) for stat in stats]))

    @classmethod
    def build_stats_export(cls, row: db.Row) -> WatchlistCollectionStatsExport:
        return WatchlistCollectionStatsExport(
            name=row["name"],
            slug=row[SLUG],
            title_count=row["title_count"],
            review_count=row["review_count"],
        )

    @classmethod
    def export(cls) -> None:
        logger.log("==== Begin exporting {}...", "watchlist collections")

        rows = db.exec_query(
            """
            SELECT
                collection_name AS 'name'
              , count(movies.imdb_id) AS 'title_count'
              , count(DISTINCT(reviews.movie_imdb_id)) AS 'review_count'
              , watchlist.slug
            FROM watchlist
            LEFT JOIN movies ON watchlist.movie_imdb_id = movies.imdb_id
            LEFT JOIN reviews ON reviews.movie_imdb_id = watchlist.movie_imdb_id
            WHERE collection_name IS NOT NULL
            GROUP BY
                collection_name
            ORDER BY
                collection_name;
          """
        )  # noqa: WPS355

        stats = []

        for row in rows:
            stats.append(cls.build_stats_export(row))

        cls.write_file(stats=stats)


class PersonStatsExporter(object):
    @classmethod
    def write_file(cls, person_type, stats: List[WatchlistPersonStatsExport]) -> None:
        file_path = os.path.join("export", "watchlist_{0}s.json".format(person_type))

        with open(file_path, "w") as output_file:
            output_file.write(json.dumps([asdict(stat) for stat in stats]))

    @classmethod
    def build_stats_export(cls, row: db.Row) -> WatchlistPersonStatsExport:
        name = row["name"]
        if row[IMDB_ID] == ETHAN_COEN_IMDB_ID:
            name = "The Coen Brothers"

        return WatchlistPersonStatsExport(
            imdb_id=row[IMDB_ID],
            name=name,
            slug=row[SLUG],
            title_count=row["title_count"],
            review_count=row["review_count"],
        )

    @classmethod
    def export(cls, person_type: str) -> None:
        logger.log("==== Begin exporting {}...", "watchlist {0}s".format(person_type))

        rows = db.exec_query(
            """
            SELECT
                {0}s.imdb_id AS 'imdb_id'
            , {0}s.full_name AS 'name'
            , count(movies.imdb_id) AS 'title_count'
            , count(DISTINCT(reviews.movie_imdb_id)) AS 'review_count'
            , watchlist.slug
            FROM watchlist
            LEFT JOIN movies ON watchlist.movie_imdb_id = movies.imdb_id
            LEFT JOIN reviews ON reviews.movie_imdb_id = watchlist.movie_imdb_id
            LEFT JOIN people AS {0}s ON {0}_imdb_id = {0}s.imdb_id
            WHERE {0}_imdb_id IS NOT NULL
            GROUP BY
                {0}_imdb_id
            ORDER BY
                {0}s.full_name;
          """.format(
                person_type
            )
        )  # noqa: WPS355

        stats = []

        for row in rows:
            stats.append(cls.build_stats_export(row))

        cls.write_file(stats=stats, person_type=person_type)


class MoviesExporter(object):
    @classmethod
    def write_file(cls, titles: List[WatchlistTitleExport]) -> None:
        file_path = os.path.join("export", "watchlist_movies.json")

        with open(file_path, "w") as output_file:
            output_file.write(json.dumps([asdict(title) for title in titles]))

    @classmethod
    def build_director_export(cls, row: db.Row) -> WatchlistPersonExport:
        name = row["director_name"]
        if row[DIRECTOR_IMDB_ID] == ETHAN_COEN_IMDB_ID:
            name = "The Coen Brothers"

        return WatchlistPersonExport(
            imdb_id=row["director_imdb_id"],
            name=name,
            slug=row[SLUG],
        )

    @classmethod
    def export(cls) -> None:
        logger.log("==== Begin exporting {}...", "watchlist movies")

        rows = db.exec_query(
            """
            SELECT
            movies.imdb_id
            , title
            , year
            , release_date
            , sort_title
            , directors.imdb_id AS 'director_imdb_id'
            , directors.full_name AS 'director_name'
            , performers.imdb_id AS 'performer_imdb_id'
            , performers.full_name AS 'performer_name'
            , writers.imdb_id AS 'writer_imdb_id'
            , writers.full_name AS 'writer_name'
            , collection_name AS 'collection'
            , slug
            FROM watchlist
            LEFT JOIN movies ON watchlist.movie_imdb_id = movies.imdb_id
            LEFT JOIN release_dates ON release_dates.movie_imdb_id = movies.imdb_id
            LEFT JOIN people AS directors ON director_imdb_id = directors.imdb_id
            LEFT JOIN people AS performers ON performer_imdb_id = performers.imdb_id
            LEFT JOIN people AS writers ON writer_imdb_id = writers.imdb_id
            LEFT JOIN sort_titles on sort_titles.movie_imdb_id = watchlist.movie_imdb_id
            ORDER BY
                release_date ASC
            , movies.imdb_id ASC;
        """
        )  # noqa: WPS355

        titles: Dict[str, WatchlistTitleExport] = {}

        for row in rows:
            title = titles.setdefault(
                row[IMDB_ID],
                WatchlistTitleExport(
                    imdb_id=row[IMDB_ID],
                    title=row["title"],
                    year=row["year"],
                    sort_title=row["sort_title"],
                    release_date=row["release_date"],
                    directors=[],
                    performers=[],
                    writers=[],
                    collections=[],
                ),
            )

            if row[DIRECTOR_IMDB_ID]:
                title.directors.append(cls.build_director_export(row))

            if row["performer_imdb_id"]:
                title.performers.append(
                    WatchlistPersonExport(
                        imdb_id=row["performer_imdb_id"],
                        name=row["performer_name"],
                        slug=row[SLUG],
                    )
                )

            if row["writer_imdb_id"]:
                title.writers.append(
                    WatchlistPersonExport(
                        imdb_id=row["writer_imdb_id"],
                        name=row["writer_name"],
                        slug=row[SLUG],
                    )
                )

            if row["collection"]:
                title.collections.append(
                    WatchlistCollectionExport(name=row["collection"], slug=row["slug"])
                )

        cls.write_file(titles=list(titles.values()))
