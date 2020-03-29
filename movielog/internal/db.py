import sqlite3
from contextlib import contextmanager
from os import path
from typing import Generator

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
