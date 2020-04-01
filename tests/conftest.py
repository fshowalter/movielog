import sqlite3
from typing import Callable, Generator

import pytest

from movielog import db
from tests import typehints

TEST_DB_PATH = "file:test_db?mode=memory&cache=shared"


@pytest.fixture(autouse=True)
def set_sqlite3_to_use_in_memory_db() -> Generator[None, None, None]:
    """ Hold an open connection for the length of a test to persist the
    in-memory db."""
    db.DB_PATH = TEST_DB_PATH
    db.DbConnectionOpts = {"uri": True}
    connection = sqlite3.connect(TEST_DB_PATH, uri=True)
    yield
    connection.close()


@pytest.fixture
def sql_connection() -> Generator[sqlite3.Connection, None, None]:
    connection = sqlite3.connect(TEST_DB_PATH, uri=True)
    connection.row_factory = sqlite3.Row
    yield connection
    connection.close()


@pytest.fixture
def get_table_info() -> Callable[..., typehints.TableInfoType]:
    def _get_table_info(name: str) -> typehints.TableInfoType:
        connection = sqlite3.connect(TEST_DB_PATH, uri=True)
        connection.row_factory = sqlite3.Row
        rows = connection.execute(f"PRAGMA table_info('{name}')").fetchall()
        connection.close()
        table_info: typehints.TableInfoType = []
        for row in rows:
            table_info.append(
                (
                    row["cid"],
                    row["name"],
                    row["type"],
                    row["notnull"],
                    row["dflt_value"],
                    row["pk"],
                )
            )
        return table_info

    return _get_table_info
