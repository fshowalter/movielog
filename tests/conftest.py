from __future__ import annotations

import os
import sqlite3
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.repository import imdb_http, markdown_viewings
from movielog.repository.datasets import downloader
from movielog.repository.db import db

TEST_DB_PATH = "file:test_db?mode=memory&cache=shared"


@pytest.fixture(autouse=True)
def set_sqlite3_to_use_in_memory_db() -> Generator[None]:
    """Hold an open connection for the length of a test to persist the
    in-memory db."""
    db.DB_PATH = TEST_DB_PATH
    db.DbConnectionOpts = {"uri": True}
    connection = sqlite3.connect(TEST_DB_PATH, uri=True)
    yield
    connection.close()


original_download_dir = downloader.DOWNLOAD_DIR
original_viewings_dir = markdown_viewings.FOLDER_NAME


@pytest.fixture(autouse=True)
def mock_cinemagoer_imdb_http_get_person(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(imdb_http.imdb_http, "get_person")


@pytest.fixture(autouse=True)
def mock_cinemagoer_imdb_http_get_movie(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(imdb_http.imdb_http, "get_movie")


@pytest.fixture(autouse=True)
def mock_download_dir(mocker: MockerFixture, tmp_path: Path) -> None:
    mocker.patch(
        "movielog.repository.datasets.downloader.DOWNLOAD_DIR",
        tmp_path / original_download_dir,
    )


@pytest.fixture(autouse=True)
def mock_exports_folder_name(mocker: MockerFixture, tmp_path: Path) -> None:
    mocker.patch("movielog.exports.exporter.EXPORT_FOLDER_NAME", tmp_path / "export")


@pytest.fixture(autouse=True)
def mock_reviews_folder_name(mocker: MockerFixture, tmp_path: Path) -> None:
    mocker.patch("movielog.repository.markdown_reviews.FOLDER_NAME", tmp_path)


@pytest.fixture(autouse=True)
def mock_viewings_folder_name(mocker: MockerFixture, tmp_path: Path) -> None:
    mocker.patch(
        "movielog.repository.markdown_viewings.FOLDER_NAME",
        tmp_path / original_viewings_dir,
    )


@pytest.fixture(autouse=True)
def mock_watchlist_serializer_folder_name(mocker: MockerFixture, tmp_path: Path) -> None:
    mocker.patch(
        "movielog.repository.watchlist_serializer.FOLDER_NAME",
        os.path.join(tmp_path, "directors"),
    )


@pytest.fixture(autouse=True)
def mock_titles_data_folder_name(mocker: MockerFixture, tmp_path: Path) -> None:
    mocker.patch("movielog.repository.json_titles.FOLDER_NAME", tmp_path)


def dict_factory(cursor: sqlite3.Cursor, row: tuple[Any, ...]) -> dict[str, Any]:
    row_dict = {}
    for index, column in enumerate(cursor.description):
        row_dict[column[0]] = row[index]
    return row_dict


QueryResult = list[dict[str, Any]]


@pytest.fixture
def sql_query() -> Callable[[str], QueryResult]:
    def factory(query: str) -> QueryResult:
        connection = sqlite3.connect(TEST_DB_PATH, uri=True)
        connection.row_factory = dict_factory
        query_results = connection.execute(query).fetchall()
        connection.close()

        return query_results

    return factory
