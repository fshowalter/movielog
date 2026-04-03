from __future__ import annotations

import sqlite3
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from movielog.repository import markdown_viewings
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
def mock_imdb_http_get_title(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr("movielog.repository.imdb_http_title.get_title_page", mock)
    return mock


@pytest.fixture(autouse=True)
def mock_imdb_http_get_director(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr("movielog.repository.imdb_http_director.get_director", mock)
    return mock


@pytest.fixture(autouse=True)
def mock_imdb_http_get_performer(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr("movielog.repository.imdb_http_performer.get_performer", mock)
    return mock


@pytest.fixture(autouse=True)
def mock_imdb_http_get_writer(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr("movielog.repository.imdb_http_writer.get_writer", mock)
    return mock


@pytest.fixture(autouse=True)
def mock_download_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "movielog.repository.datasets.downloader.DOWNLOAD_DIR",
        tmp_path / original_download_dir,
    )


@pytest.fixture(autouse=True)
def mock_exports_folder_name(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr("movielog.exports.exporter.EXPORT_FOLDER_NAME", tmp_path / "export")


@pytest.fixture(autouse=True)
def mock_reviews_folder_name(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr("movielog.repository.markdown_reviews.FOLDER_NAME", tmp_path)


@pytest.fixture(autouse=True)
def mock_viewings_folder_name(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "movielog.repository.markdown_viewings.FOLDER_NAME",
        tmp_path / original_viewings_dir,
    )


@pytest.fixture(autouse=True)
def mock_watchlist_serializer_folder_name(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "movielog.repository.watchlist_serializer.FOLDER_NAME",
        tmp_path / "watchlist",
    )


@pytest.fixture(autouse=True)
def mock_titles_data_folder_name(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr("movielog.repository.json_titles.FOLDER_NAME", tmp_path)


@pytest.fixture(autouse=True)
def mock_collections_folder_name(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "movielog.repository.json_collections.FOLDER_NAME", tmp_path / "collections"
    )


@pytest.fixture(autouse=True)
def mock_needs_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("movielog.cli.ask_for_token.NEEDS_TOKEN", True)


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
