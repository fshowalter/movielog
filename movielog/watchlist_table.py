from dataclasses import asdict, dataclass
from typing import Callable, Dict, List, Optional, Sequence, Type

from movielog import db, watchlist_collection, watchlist_person
from movielog.logger import logger

TABLE_NAME = "watchlist"
SLUG = "slug"
DIRECTOR_IMDB_ID = "director_imdb_id"
ETHAN_COEN_IMDB_ID = "nm0001053"


@dataclass
class Movie(object):
    movie_imdb_id: str
    slug: str
    director_imdb_id: Optional[str] = None
    performer_imdb_id: Optional[str] = None
    writer_imdb_id: Optional[str] = None
    collection_name: Optional[str] = None

    @classmethod
    def movies_for_collection(
        cls, collection: watchlist_collection.Collection
    ) -> List["Movie"]:
        movies = []

        for collection_movie in collection.movies:
            movies.append(
                cls(
                    movie_imdb_id=collection_movie.imdb_id,
                    collection_name=collection.name,
                    slug=collection.slug,
                )
            )

        return movies

    @classmethod
    def movies_for_person(cls, person: watchlist_person.Person) -> List["Movie"]:
        movies = []

        type_map: Dict[
            Type[watchlist_person.Person],
            Callable[[watchlist_person.Movie], Movie],
        ] = {
            watchlist_person.Director: lambda movie: cls(
                movie_imdb_id=movie.imdb_id,
                director_imdb_id=person.imdb_id,
                slug=person.slug,
            ),
            watchlist_person.Performer: lambda movie: cls(
                movie_imdb_id=movie.imdb_id,
                performer_imdb_id=person.imdb_id,
                slug=person.slug,
            ),
            watchlist_person.Writer: lambda movie: cls(
                movie_imdb_id=movie.imdb_id,
                writer_imdb_id=person.imdb_id,
                slug=person.slug,
            ),
        }

        for person_movie in person.movies:
            movie = type_map[type(person)]

            movies.append(movie(person_movie))

        return movies


class WatchlistTable(db.Table):
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
    def insert_watchlist_movies(cls, titles: Sequence[Movie]) -> None:
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
def update(watchlist_movies: Sequence[Movie]) -> None:
    logger.log("==== Begin updating {}...", TABLE_NAME)

    WatchlistTable.recreate()
    WatchlistTable.insert_watchlist_movies(watchlist_movies)
