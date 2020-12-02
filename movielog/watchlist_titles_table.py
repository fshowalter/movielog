from dataclasses import asdict, dataclass
from typing import Callable, Dict, List, Optional, Set, Type

from movielog import db, watchlist_collection, watchlist_person
from movielog.logger import logger

TABLE_NAME = "watchlist_titles"
SLUG = "slug"
DIRECTOR_IMDB_ID = "director_imdb_id"
ETHAN_COEN_IMDB_ID = "nm0001053"


@dataclass
class WatchlistTitle(object):
    movie_imdb_id: str
    slug: str
    director_imdb_id: Optional[str] = None
    performer_imdb_id: Optional[str] = None
    writer_imdb_id: Optional[str] = None
    collection_name: Optional[str] = None
    sort_title: Optional[str] = None

    @classmethod
    def build_sort_title(cls, title: str) -> str:
        title_lower = title.lower()
        title_words = title.split(" ")
        lower_words = title_lower.split(" ")
        articles = set(["a", "an", "the"])

        if (len(title_words) > 1) and (lower_words[0] in articles):
            return "{0}, {1}".format(
                " ".join(title_words[1 : len(title_words)]), title_words[0]
            )

        return title

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
                    sort_title=cls.build_sort_title(collection_title.title),
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
                sort_title=cls.build_sort_title(title.title),
            ),
            watchlist_person.Performer: lambda title: cls(
                movie_imdb_id=title.imdb_id,
                performer_imdb_id=person.imdb_id,
                slug=person.slug,
                sort_title=cls.build_sort_title(title.title),
            ),
            watchlist_person.Writer: lambda title: cls(
                movie_imdb_id=title.imdb_id,
                writer_imdb_id=person.imdb_id,
                slug=person.slug,
                sort_title=cls.build_sort_title(title.title),
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
            "sort_title" TEXT,
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
              sort_title,
              slug)
          VALUES(
              :movie_imdb_id,
              :director_imdb_id,
              :performer_imdb_id,
              :writer_imdb_id,
              :collection_name,
              :sort_title,
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


def load_all(update_from_imdb: bool = False) -> List[WatchlistTitle]:
    titles: List[WatchlistTitle] = []

    for collection in watchlist_collection.all_items():
        titles.extend(WatchlistTitle.titles_for_collection(collection))

    person_types = [
        watchlist_person.Director,
        watchlist_person.Performer,
        watchlist_person.Writer,
    ]

    for person_type in person_types:
        if update_from_imdb:
            person_type.refresh_all_item_titles()

        for person in person_type.all_items():
            titles.extend(WatchlistTitle.titles_for_person(person))

    return titles


@logger.catch
def update() -> None:
    logger.log("==== Begin updating {}...", TABLE_NAME)

    WatchlistTitlesTable.recreate()
    WatchlistTitlesTable.insert_watchlist_titles(load_all(update_from_imdb=True))


def imdb_ids() -> Set[str]:
    return set([title.movie_imdb_id for title in load_all()])
