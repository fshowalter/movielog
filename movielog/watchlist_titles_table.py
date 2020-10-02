import json
import os
from dataclasses import asdict, dataclass
from typing import Callable, Dict, List, Optional, Type

from movielog import db, watchlist_collection, watchlist_person
from movielog.logger import logger

TABLE_NAME = "watchlist_titles"
SLUG = "slug"


@dataclass
class WatchlistTitle(object):
    movie_imdb_id: str
    slug: str
    director_imdb_id: Optional[str] = None
    performer_imdb_id: Optional[str] = None
    writer_imdb_id: Optional[str] = None
    collection_name: Optional[str] = None

    @classmethod
    def titles_for_collection(
        cls, collection: watchlist_collection.Collection
    ) -> List["WatchlistTitle"]:
        titles = []

        for collection_title in collection.titles:
            titles.append(
                cls(
                    movie_imdb_id=collection_title.imdb_id,
                    collection_name=collection.name,
                    slug=collection.slug,
                )
            )

        return titles

    @classmethod
    def titles_for_person(
        cls, person: watchlist_person.Person
    ) -> List["WatchlistTitle"]:
        titles = []

        type_map: Dict[
            Type[watchlist_person.Person],
            Callable[[watchlist_person.PersonTitle], WatchlistTitle],
        ] = {
            watchlist_person.Director: lambda title: cls(
                movie_imdb_id=title.imdb_id,
                director_imdb_id=person.imdb_id,
                slug=person.slug,
            ),
            watchlist_person.Performer: lambda title: cls(
                movie_imdb_id=title.imdb_id,
                performer_imdb_id=person.imdb_id,
                slug=person.slug,
            ),
            watchlist_person.Writer: lambda title: cls(
                movie_imdb_id=title.imdb_id,
                writer_imdb_id=person.imdb_id,
                slug=person.slug,
            ),
        }

        for person_title in person.titles:
            title = type_map[person.__class__]

            titles.append(title(person_title))

        return titles


class WatchlistTitlesTable(db.Table):
    table_name = TABLE_NAME

    recreate_ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "{0}" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            "movie_imdb_id" TEXT NOT NULL
                REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "director_imdb_id" TEXT
                REFERENCES people(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "performer_imdb_id" TEXT
                REFERENCES people(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "writer_imdb_id" TEXT
                REFERENCES people(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "collection_name" TEXT,
            "slug" TEXT NOT NULL);
        """

    @classmethod
    def insert_watchlist_titles(cls, titles: List[WatchlistTitle]) -> None:
        ddl = """
          INSERT INTO {0}(
              movie_imdb_id,
              director_imdb_id,
              performer_imdb_id,
              writer_imdb_id,
              collection_name,
              slug)
          VALUES(
              :movie_imdb_id,
              :director_imdb_id,
              :performer_imdb_id,
              :writer_imdb_id,
              :collection_name,
              :slug);
        """.format(
            TABLE_NAME
        )

        parameter_seq = [asdict(title) for title in titles]

        cls.insert(ddl=ddl, parameter_seq=parameter_seq)
        cls.add_index("movie_imdb_id")
        cls.add_index("director_imdb_id")
        cls.add_index("performer_imdb_id")
        cls.add_index("writer_imdb_id")
        cls.validate(titles)


@logger.catch
def update() -> None:
    logger.log("==== Begin updating {}...", TABLE_NAME)

    WatchlistTitlesTable.recreate()

    titles: List[WatchlistTitle] = []

    for collection in watchlist_collection.all_items():
        titles.extend(WatchlistTitle.titles_for_collection(collection))

    person_types = [
        watchlist_person.Director,
        watchlist_person.Performer,
        watchlist_person.Writer,
    ]

    for person_type in person_types:
        person_type.refresh_all_item_titles()

        for person in person_type.all_items():
            titles.extend(WatchlistTitle.titles_for_person(person))

    WatchlistTitlesTable.insert_watchlist_titles(titles)


@dataclass
class WatchlistPersonExport(object):
    imdb_id: str
    name: str
    slug: str


@dataclass
class WatchlistCollectionExport(object):
    name: str
    slug: str


@dataclass
class WatchlistTitleExport(object):
    imdb_id: str
    title: str
    year: str
    release_date: str
    directors: List[WatchlistPersonExport]
    performers: List[WatchlistPersonExport]
    writers: List[WatchlistPersonExport]
    collections: List[WatchlistCollectionExport]


def export() -> None:
    Exporter.export()


class Exporter(object):
    @classmethod
    def write_file(cls, titles: List[WatchlistTitleExport]) -> None:
        file_path = os.path.join("export", "watchlist_titles.json")

        with open(file_path, "w") as output_file:
            output_file.write(json.dumps([asdict(title) for title in titles]))

    @classmethod
    def export(cls) -> None:
        logger.log("==== Begin exporting {}...", TABLE_NAME)
        query = """
            SELECT
            movies.imdb_id
            , title
            , year
            , release_date
            , directors.imdb_id AS 'director_imdb_id'
            , directors.full_name AS 'director_name'
            , performers.imdb_id AS 'performer_imdb_id'
            , performers.full_name AS 'performer_name'
            , writers.imdb_id AS 'writer_imdb_id'
            , writers.full_name AS 'writer_name'
            , collection_name AS 'collection'
            , slug
            FROM watchlist_titles
            LEFT JOIN movies ON watchlist_titles.movie_imdb_id = movies.imdb_id
            LEFT JOIN release_dates ON release_dates.movie_imdb_id = movies.imdb_id
            LEFT JOIN people AS directors ON director_imdb_id = directors.imdb_id
            LEFT JOIN people AS performers ON performer_imdb_id = performers.imdb_id
            LEFT JOIN people AS writers ON writer_imdb_id = writers.imdb_id
            ORDER BY
                year ASC
            , movies.imdb_id ASC;
        """

        rows = db.exec_query(query)

        titles: Dict[str, WatchlistTitleExport] = {}

        for row in rows:
            title = titles.setdefault(
                row["imdb_id"],
                WatchlistTitleExport(
                    imdb_id=row["imdb_id"],
                    title=row["title"],
                    year=row["year"],
                    release_date=row["release_date"],
                    directors=[],
                    performers=[],
                    writers=[],
                    collections=[],
                ),
            )

            if row["director_imdb_id"]:
                title.directors.append(
                    WatchlistPersonExport(
                        imdb_id=row["director_imdb_id"],
                        name=row["director_name"],
                        slug=row[SLUG],
                    )
                )

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
