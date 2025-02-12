from __future__ import annotations

import sqlite3
from collections.abc import Callable, Generator, Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from movielog.repository import format_tools
from movielog.utils.logging import logger

DB_FILE_NAME = "movie_db.sqlite3"
DB_DIR = "db"

Connection = sqlite3.Connection
Cursor = sqlite3.Cursor
Row = sqlite3.Row

DB_PATH = str(Path(DB_DIR) / DB_FILE_NAME)
DbConnectionOpts: dict[str, Any] = {"isolation_level": None}
RowFactory = Callable[[sqlite3.Cursor, tuple[Any, ...]], Any]


@contextmanager
def connect() -> Generator[Connection]:
    connection = sqlite3.connect(DB_PATH, **DbConnectionOpts)
    yield connection
    connection.close()


@contextmanager
def transaction(connection: Connection) -> Generator[None]:
    connection.execute("PRAGMA journal_mode = WAL;")
    connection.execute("BEGIN TRANSACTION;")
    yield
    connection.commit()
    connection.execute("PRAGMA journal_mode = DELETE")


def add_index(table_name: str, column: str) -> None:
    ddl = """
        DROP INDEX IF EXISTS "index_{0}_on_{1}";
        CREATE INDEX "index_{0}_on_{1}" ON "{0}" ("{1}");
    """

    logger.log("Add index to table {} on column {}...", table_name, column)
    execute_script(ddl.format(table_name, column))


def validate_row_count(table_name: str, expected: int) -> None:
    actual = fetch_one(f"select count(*) as count from {table_name}")["count"]
    assert expected == actual
    logger.log(
        "Table {} contains {} rows.", table_name, format_tools.humanize_int(actual)
    )


def insert_into_table(
    table_name: str, insert_ddl: str, rows: Sequence[Mapping[str, Any]]
) -> None:
    logger.log(
        "Inserting {} rows into {}...", format_tools.humanize_int(len(rows)), table_name
    )
    execute_many(insert_ddl, rows)


def recreate_table(table_name: str, table_ddl: str) -> None:
    ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "{0}" ({1});
    """

    logger.log("Recreating {} table...", table_name)
    execute_script(ddl.format(table_name, table_ddl))


def execute_script(ddl: str) -> None:
    with connect() as connection:
        connection.executescript(ddl)


def execute_many(ddl: str, parameter_seq: Sequence[Mapping[str, Any]]) -> None:
    with connect() as connection, transaction(connection):
        connection.executemany(ddl, parameter_seq)


def fetch_one(query: str, row_factory: RowFactory = sqlite3.Row) -> Any:
    with connect() as connection:
        connection.row_factory = row_factory
        return connection.execute(query).fetchone()


def fetch_all(query: str, row_factory: RowFactory = sqlite3.Row) -> list[Any]:
    with connect() as connection:
        connection.row_factory = row_factory
        return connection.execute(query).fetchall()
