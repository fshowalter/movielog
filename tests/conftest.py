from __future__ import annotations

import os
import sqlite3
from typing import Any, Callable, Generator, Tuple

import pytest
from pytest_mock import MockerFixture

from movielog import db
from movielog.moviedata.core import downloader
from testtools.types import QueryResult

TEST_DB_PATH = "file:test_db?mode=memory&cache=shared"


@pytest.fixture(autouse=True)
def set_sqlite3_to_use_in_memory_db() -> Generator[None, None, None]:
    """Hold an open connection for the length of a test to persist the
    in-memory db."""
    db.DB_PATH = TEST_DB_PATH
    db.DbConnectionOpts = {"uri": True}
    connection = sqlite3.connect(TEST_DB_PATH, uri=True)
    yield
    connection.close()


original_download_dir = downloader.DOWNLOAD_DIR


@pytest.fixture(autouse=True)
def mock_download_path(mocker: MockerFixture, tmp_path: str) -> None:
    mocker.patch(
        "movielog.moviedata.core.downloader.DOWNLOAD_DIR",
        os.path.join(tmp_path, original_download_dir),
    )


@pytest.fixture(autouse=True)
def mock_reviews_folder_path(mocker: MockerFixture, tmp_path: str) -> None:
    mocker.patch("movielog.reviews.serializer.FOLDER_NAME", tmp_path)


@pytest.fixture(autouse=True)
def mock_viewings_folder_path(mocker: MockerFixture, tmp_path: str) -> None:
    mocker.patch("movielog.viewings.serializer.FOLDER_NAME", tmp_path)


def dict_factory(cursor: sqlite3.Cursor, row: Tuple[Any, ...]) -> dict[str, Any]:
    row_dict = {}
    for index, column in enumerate(cursor.description):
        row_dict[column[0]] = row[index]
    return row_dict


@pytest.fixture
def sql_query() -> Callable[[str], QueryResult]:
    def factory(query: str) -> QueryResult:
        connection = sqlite3.connect(TEST_DB_PATH, uri=True)
        connection.row_factory = dict_factory
        query_results = connection.execute(query).fetchall()
        connection.close()

        return query_results

    return factory
