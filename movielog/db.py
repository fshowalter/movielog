import abc
import sqlite3
from contextlib import contextmanager
from os import path
from typing import Any, Dict, Generator, List, Sized

from movielog import humanize
from movielog.logger import logger

DB_FILE_NAME = "movie_db.sqlite3"
DB_DIR = "db"

Connection = sqlite3.Connection
Cursor = sqlite3.Cursor


@contextmanager
def connect() -> Generator[sqlite3.Connection, None, None]:
    connection = sqlite3.connect(path.join(DB_DIR, DB_FILE_NAME), isolation_level=None)
    connection.row_factory = sqlite3.Row
    yield connection
    connection.close()


@contextmanager
def transaction(connection: sqlite3.Connection) -> Generator[None, None, None]:
    connection.execute("PRAGMA journal_mode = WAL;")
    connection.execute("BEGIN TRANSACTION;")
    yield
    connection.commit()
    connection.execute("PRAGMA journal_mode = DELETE")


class Table(abc.ABC):
    recreate_ddl: str
    table_name: str

    @classmethod
    def add_index(cls, column: str) -> None:
        with connect() as connection:
            connection.executescript(
                """
                DROP INDEX IF EXISTS "index_{0}_on_{1}";
                CREATE INDEX "index_{0}_on_{1}" ON "{0}" ("{1}");
                """.format(
                    cls.table_name, column
                ),
            )

    @classmethod
    def validate(cls, collection: Sized) -> None:
        with connect() as connection:
            inserted = connection.execute(
                "select count(*) from {0}".format(cls.table_name),  # noqa: S608
            ).fetchone()[0]

            assert collection

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
