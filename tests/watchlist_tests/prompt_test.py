import os

import pytest
from pytest_mock import MockerFixture

from movielog import watchlist

Collection = watchlist.Collection


@pytest.fixture(autouse=True)
def mock_watchlist_path(mocker: MockerFixture, tmp_path: str) -> str:
    watchlist_path = tmp_path
    mocker.patch("movielog.watchlist_person.WATCHLIST_PATH", watchlist_path)
    mocker.patch("movielog.watchlist_collection.WATCHLIST_PATH", watchlist_path)
    return watchlist_path


EXPECTED = "frozen: false\nname: Orson Welles\nimdb_id: nm0000080\nslug: orson-welles\ntitles: []\n"


def test_add_director_creates_director(
    mock_watchlist_path: str,
    mocker: MockerFixture,
) -> None:
    watchlist.add_director(imdb_id="nm0000080", name="Orson Welles")

    with open(
        os.path.join(mock_watchlist_path, "directors", "orson-welles.yml"), "r"
    ) as output_file:
        yaml_content = output_file.read()

    assert yaml_content == EXPECTED


def test_add_writer_creates_writer(
    mock_watchlist_path: str,
    mocker: MockerFixture,
) -> None:
    watchlist.add_writer(imdb_id="nm0000080", name="Orson Welles")

    with open(
        os.path.join(mock_watchlist_path, "writers", "orson-welles.yml"), "r"
    ) as output_file:
        yaml_content = output_file.read()

    assert yaml_content == EXPECTED


def test_add_performer_creates_performer(
    mock_watchlist_path: str,
    mocker: MockerFixture,
) -> None:
    watchlist.add_performer(imdb_id="nm0000080", name="Orson Welles")

    with open(
        os.path.join(mock_watchlist_path, "performers", "orson-welles.yml"), "r"
    ) as output_file:
        yaml_content = output_file.read()

    assert yaml_content == EXPECTED


def test_add_collection_creates_new_collection(
    mock_watchlist_path: str, mocker: MockerFixture
) -> None:
    expected = "frozen: false\nname: Halloween\nslug: halloween\ntitles: []\n"

    watchlist.add_collection(name="Halloween")

    with open(
        os.path.join(mock_watchlist_path, "collections", "halloween.yml"), "r"
    ) as output_file:
        yaml_content = output_file.read()

    assert yaml_content == expected


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


def test_update_watchlist_titles_table_calls_update_on_watchlist_titles_table(
    mocker: MockerFixture,
) -> None:
    mock_watchlist_titles_table_update = mocker.patch(
        "movielog.watchlist.watchlist_titles_table.update"
    )

    watchlist.update_watchlist_titles_table()

    mock_watchlist_titles_table_update.assert_called_once()
