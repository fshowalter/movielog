import abc
import sqlite3
from contextlib import contextmanager
from os import path
from typing import Any, Dict, Generator, List, Sequence, Sized

from movielog import humanize
from movielog.logger import logger

DB_FILE_NAME = "movie_db.sqlite3"
DB_DIR = "db"

Connection = sqlite3.Connection
Cursor = sqlite3.Cursor
Row = sqlite3.Row

DB_PATH = path.join(DB_DIR, DB_FILE_NAME)
DbConnectionOpts: Dict[str, Any] = {"isolation_level": None}


@contextmanager
def connect() -> Generator[Connection, None, None]:
    connection = sqlite3.connect(DB_PATH, **DbConnectionOpts)
    connection.row_factory = sqlite3.Row
    yield connection
    connection.close()


@contextmanager
def transaction(connection: Connection) -> Generator[None, None, None]:
    connection.execute("PRAGMA journal_mode = WAL;")
    connection.execute("BEGIN TRANSACTION;")
    yield
    connection.commit()
    connection.execute("PRAGMA journal_mode = DELETE")


def exec_query(query: str) -> Sequence[sqlite3.Row]:
    with connect() as connection:
        return connection.execute(query).fetchall()


class Table(abc.ABC):
    recreate_ddl: str
    table_name: str

    @classmethod
    def add_index(cls, column: str) -> None:
        script = """
            DROP INDEX IF EXISTS "index_{0}_on_{1}";
            CREATE INDEX "index_{0}_on_{1}" ON "{0}" ("{1}");
        """
        with connect() as connection:
            connection.executescript(script.format(cls.table_name, column))

    @classmethod
    def validate(cls, collection: Sized) -> None:
        with connect() as connection:
            inserted = connection.execute(
                "select count(*) from {0}".format(cls.table_name),  # noqa: S608
            ).fetchone()[0]

            assert collection  # noqa: S101

            expected = len(collection)
            assert expected == inserted  # noqa: S101

            logger.log("Inserted {} {}.", humanize.intcomma(inserted), cls.table_name)

    @classmethod
    def recreate(cls) -> None:
        formatted_ddl = cls.recreate_ddl.format(cls.table_name)
        with connect() as connection:
            logger.log("Recreating {} table...", cls.table_name)
            connection.executescript(formatted_ddl)

    @classmethod
    def insert(cls, ddl: str, parameter_seq: List[Dict[str, Any]]) -> None:
        logger.log("Inserting {}...", cls.table_name)

        with connect() as connection:
            with transaction(connection):
                connection.executemany(ddl, parameter_seq)

    @classmethod
    def delete(cls, key: str, ids: Sequence[str]) -> None:
        ddl = """
            DELETE FROM {0} WHERE {1} IN ({2});
        """

        with connect() as connection:
            with transaction(connection):
                connection.execute(ddl.format(cls.table_name, key, cls.format_ids(ids)))
                logger.log(
                    "Deleted {} rows from {}...",
                    humanize.intcomma(len(ids)),
                    cls.table_name,
                )

    @classmethod
    def format_ids(cls, ids: Sequence[str]) -> str:
        return ",".join('"{0}"'.format(db_id) for db_id in ids)
