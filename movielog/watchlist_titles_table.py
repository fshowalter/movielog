from dataclasses import asdict, dataclass
from typing import List, Optional

from movielog import db, watchlist_collection, watchlist_person
from movielog.logger import logger

TABLE_NAME = "watchlist_titles"

Query = """
    SELECT
        year,
        title,
        movie_imdb_id,
        GROUP_CONCAT(directors.full_name, '|'),
        GROUP_CONCAT(director_imdb_id, ','),
        GROUP_CONCAT(performers.full_name, '|'),
        GROUP_CONCAT(performer_imdb_id, ','),
        GROUP_CONCAT(writers.full_name, '|'),
        GROUP_CONCAT(writer_imdb_id, ','),
        GROUP_CONCAT(collection_name, '|') AS collection_names
        FROM watchlist_titles
            LEFT JOIN movies ON movie_imdb_id = movies.imdb_id
            LEFT JOIN people AS directors ON director_imdb_id = directors.imdb_id
            LEFT JOIN people AS performers ON performer_imdb_id = performers.imdb_id
            LEFT JOIN people AS writers ON writer_imdb_id = writers.imdb_id
            GROUP BY (movie_imdb_id) HAVING year < 1930 ORDER BY year;
"""


class WatchlistTitlesTableError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


@dataclass
class WatchlistTitle(object):
    movie_imdb_id: str
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
                )
            )

        return titles

    @classmethod
    def titles_for_person(
        cls, person: watchlist_person.Person
    ) -> List["WatchlistTitle"]:
        titles = []

        for person_title in person.titles:

            if isinstance(person, watchlist_person.Director):
                title = cls(
                    movie_imdb_id=person_title.imdb_id, director_imdb_id=person.imdb_id,
                )
            elif isinstance(person, watchlist_person.Performer):
                title = cls(
                    movie_imdb_id=person_title.imdb_id,
                    performer_imdb_id=person.imdb_id,
                )
            elif isinstance(person, watchlist_person.Writer):
                title = cls(
                    movie_imdb_id=person_title.imdb_id, writer_imdb_id=person.imdb_id,
                )
            else:
                WatchlistTitlesTableError(
                    "{0} is not a recognized Person instance".format(person.__class__)
                )

            titles.append(title)

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
            "collection_name" TEXT);
        """

    @classmethod
    def insert_watchlist_titles(cls, titles: List[WatchlistTitle]) -> None:
        ddl = """
          INSERT INTO {0}(
              movie_imdb_id,
              director_imdb_id,
              performer_imdb_id,
              writer_imdb_id,
              collection_name)
          VALUES(
              :movie_imdb_id,
              :director_imdb_id,
              :performer_imdb_id,
              :writer_imdb_id,
              :collection_name);
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
