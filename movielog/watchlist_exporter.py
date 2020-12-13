import json
import os
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Sequence

from typing_extensions import Protocol

from movielog import db, watchlist, watchlist_table
from movielog.logger import logger

SLUG = "slug"
DIRECTOR_IMDB_ID = "director_imdb_id"
ETHAN_COEN_IMDB_ID = "nm0001053"
IMDB_ID = "imdb_id"
COLLECTION = "collection"


class Stats(Protocol):
    name: str
    slug: str
    title_count: int
    review_count: int
    entity_type: str


@dataclass
class Person(object):
    imdb_id: str
    name: str
    slug: str


@dataclass
class PersonStats(Person):
    title_count: int
    review_count: int
    entity_type: str


@dataclass
class Collection(object):
    name: str
    slug: str


@dataclass
class CollectionStats(Collection):
    title_count: int
    review_count: int
    entity_type: str = COLLECTION
    imdb_id: Optional[str] = None


@dataclass
class Movie(object):
    imdb_id: str
    title: str
    year: str
    sort_title: str
    release_date: str
    directors: List[Person]
    performers: List[Person]
    writers: List[Person]
    collections: List[Collection]


class EntitiesExporter(object):
    @classmethod
    def write_file(cls, stats: Sequence[Stats]) -> None:
        file_path = os.path.join("export", "watchlist_entities.json")

        with open(file_path, "w") as output_file:
            output_file.write(json.dumps([asdict(stat) for stat in stats]))

    @classmethod
    def build_person_stats(cls, row: db.Row, person_type: str) -> PersonStats:
        name = row["name"]
        if row[IMDB_ID] == ETHAN_COEN_IMDB_ID:
            name = "The Coen Brothers"

        return PersonStats(
            imdb_id=row[IMDB_ID],
            name=name,
            slug=row[SLUG],
            title_count=row["title_count"],
            review_count=row["review_count"],
            entity_type=person_type,
        )

    @classmethod
    def build_collection_stats(cls, row: db.Row) -> CollectionStats:
        return CollectionStats(
            name=row["name"],
            slug=row[SLUG],
            title_count=row["title_count"],
            review_count=row["review_count"],
            entity_type=COLLECTION,
        )

    @classmethod
    def fetch_person_stats(cls, person_type: str) -> Sequence[PersonStats]:
        stats = []

        person_rows = db.exec_query(
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

        for person_row in person_rows:
            stats.append(cls.build_person_stats(person_row, person_type))

        return stats

    @classmethod
    def fetch_collection_stats(cls) -> Sequence[CollectionStats]:
        stats = []

        collection_rows = db.exec_query(
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

        for collection_row in collection_rows:
            stats.append(cls.build_collection_stats(collection_row))

        return stats

    @classmethod
    def export(cls) -> None:
        logger.log("==== Begin exporting {}...", "watchlist entities")

        stats: List[Stats] = []

        for person_type in ("director", "performer", "writer"):
            stats.extend(cls.fetch_person_stats(person_type))

        stats.extend(cls.fetch_collection_stats())

        cls.write_file(stats=stats)


class MoviesExporter(object):
    @classmethod
    def write_file(cls, movies: List[Movie]) -> None:
        file_path = os.path.join("export", "watchlist_movies.json")

        with open(file_path, "w") as output_file:
            output_file.write(json.dumps([asdict(movie) for movie in movies]))

    @classmethod
    def build_director_export(cls, row: db.Row) -> Person:
        name = row["director_name"]
        if row[DIRECTOR_IMDB_ID] == ETHAN_COEN_IMDB_ID:
            name = "The Coen Brothers"

        return Person(
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

        movies: Dict[str, Movie] = {}

        for row in rows:
            movie = movies.setdefault(
                row[IMDB_ID],
                Movie(
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
                movie.directors.append(cls.build_director_export(row))

            if row["performer_imdb_id"]:
                movie.performers.append(
                    Person(
                        imdb_id=row["performer_imdb_id"],
                        name=row["performer_name"],
                        slug=row[SLUG],
                    )
                )

            if row["writer_imdb_id"]:
                movie.writers.append(
                    Person(
                        imdb_id=row["writer_imdb_id"],
                        name=row["writer_name"],
                        slug=row[SLUG],
                    )
                )

            if row["collection"]:
                movie.collections.append(
                    Collection(name=row["collection"], slug=row["slug"])
                )

        cls.write_file(movies=list(movies.values()))


def export(watchlist_movies: Sequence[watchlist.Movie]) -> None:
    watchlist_table.update(watchlist_movies)

    MoviesExporter.export()
    EntitiesExporter.export()
