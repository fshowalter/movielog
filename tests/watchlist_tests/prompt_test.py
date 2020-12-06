import json
import os
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog import watchlist

Collection = watchlist.Collection


@pytest.fixture(autouse=True)
def mock_imdb_data_update(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.imdb_data.update")


@pytest.fixture(autouse=True)
def mock_viewings_update(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.watchlist_person.refresh_credits")


@pytest.fixture(autouse=True)
def mock_director_folder_path(mocker: MockerFixture, tmp_path: str) -> str:
    mocker.patch("movielog.watchlist_person.DIRECTORS_PATH", tmp_path)
    return tmp_path


@pytest.fixture(autouse=True)
def mock_performers_path(mocker: MockerFixture, tmp_path: str) -> str:
    mocker.patch("movielog.watchlist_person.PERFORMERS_PATH", tmp_path)
    return tmp_path


@pytest.fixture(autouse=True)
def mock_writers_path(mocker: MockerFixture, tmp_path: str) -> str:
    mocker.patch("movielog.watchlist_person.WRITERS_PATH", tmp_path)
    return tmp_path


@pytest.fixture(autouse=True)
def mock_collections_path(mocker: MockerFixture, tmp_path: str) -> str:
    mocker.patch("movielog.watchlist_collection.FOLDER_PATH", tmp_path)
    return tmp_path


expected_person = {
    "frozen": False,
    "name": "Orson Welles",
    "imdb_id": "nm0000080",
    "slug": "orson-welles",
    "movies": [],
}


def test_add_director_creates_director(
    mock_director_folder_path: str,
    mocker: MockerFixture,
) -> None:
    watchlist.add_director(imdb_id="nm0000080", name="Orson Welles")

    with open(
        os.path.join(mock_director_folder_path, "orson-welles.json"), "r"
    ) as output_file:
        file_content = json.load(output_file)

    assert file_content == expected_person


def test_add_writer_creates_writer(
    mock_writers_path: str,
    mocker: MockerFixture,
) -> None:
    watchlist.add_writer(imdb_id="nm0000080", name="Orson Welles")

    with open(os.path.join(mock_writers_path, "orson-welles.json"), "r") as output_file:
        file_content = json.load(output_file)

    assert file_content == expected_person


def test_add_performer_creates_performer(
    mock_performers_path: str,
    mocker: MockerFixture,
) -> None:
    watchlist.add_performer(imdb_id="nm0000080", name="Orson Welles")

    with open(
        os.path.join(mock_performers_path, "orson-welles.json"), "r"
    ) as output_file:
        file_content = json.load(output_file)

    assert file_content == expected_person


def test_add_collection_creates_new_collection(
    mock_collections_path: str, mocker: MockerFixture
) -> None:
    expected_colleciton = {
        "name": "Halloween",
        "slug": "halloween",
        "movies": [],
    }

    watchlist.add_collection(name="Halloween")

    with open(
        os.path.join(mock_collections_path, "halloween.json"), "r"
    ) as output_file:
        file_content = json.load(output_file)

    assert file_content == expected_colleciton


def test_all_collections_returns_all_collections() -> None:
    collection1 = Collection(name="Friday the 13th")
    collection1.save()

    collection2 = Collection(name="James Bond")
    collection2.save()

    expected = [
        collection1,
        collection2,
    ]

    assert watchlist.all_collections() == expected
