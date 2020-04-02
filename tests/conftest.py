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
def sql_query() -> Callable[..., typehints.QueryResultType]:
    def _sql_query(query: str) -> typehints.QueryResultType:
        connection = sqlite3.connect(TEST_DB_PATH, uri=True)
        connection.row_factory = sqlite3.Row
        query_results = connection.execute(query).fetchall()
        connection.close()
        rows = []
        for row in query_results:
            rows.append(tuple(dict(row).values()))
        return rows

    return _sql_query
