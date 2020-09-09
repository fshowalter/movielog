from typing import Any

import pytest
from pytest_mock import MockerFixture

from movielog import watchlist_titles_table
from movielog.watchlist_collection import Collection
from movielog.watchlist_file import Title
from movielog.watchlist_person import Director, Performer, Person, Writer


@pytest.fixture(autouse=True)
def person_refresh_all_item_titles_mock(mocker: MockerFixture) -> Any:
    return mocker.patch.object(Person, "refresh_all_item_titles")


@pytest.fixture(autouse=True)
def director_all_items_mock(mocker: MockerFixture) -> Any:
    return mocker.patch.object(Director, "all_items")


@pytest.fixture(autouse=True)
def performer_all_items_mock(mocker: MockerFixture) -> Any:
    return mocker.patch.object(Performer, "all_items")


@pytest.fixture(autouse=True)
def writer_all_items_mock(mocker: MockerFixture) -> Any:
    return mocker.patch.object(Writer, "all_items")


@pytest.fixture(autouse=True)
def collection_all_items_mock(mocker: MockerFixture) -> Any:
    return mocker.patch.object(Collection, "all_items")


def test_inserts_collection_items(
    sql_query: MockerFixture,
    mocker: MockerFixture,
    person_refresh_all_item_titles_mock: MockerFixture,
    director_all_items_mock: MockerFixture,
    performer_all_items_mock: MockerFixture,
    writer_all_items_mock: MockerFixture,
    collection_all_items_mock: MockerFixture,
) -> None:
    collection_all_items_mock.return_value = [
        Collection(
            file_path=None,
            name="Nolan's Batman",
            imdb_id=None,
            titles=[
                Title(imdb_id="tt0372784", title="Batman Begins", year=2005),
                Title(imdb_id="tt0468569", title="The Dark Knight", year=2008),
                Title(imdb_id="tt1345836", title="The Dark Knight Rises", year=2012),
            ],
        )
    ]

    director_all_items_mock.return_value = [
        Director(
            file_path=None,
            name="Charles Laughton",
            imdb_id="nm0001452",
            titles=[
                Title(imdb_id="tt0048424", title="The Night of the Hunter", year=1955)
            ],
        )
    ]

    performer_all_items_mock.return_value = [
        Performer(
            file_path=None,
            name="Peter Cushing",
            imdb_id="nm0001088",
            titles=[
                Title(
                    imdb_id="tt0050280", year=1957, title="The Curse of Frankenstein"
                ),
                Title(imdb_id="tt0051554", year=1958, title="Horror of Dracula"),
            ],
        )
    ]

    writer_all_items_mock.return_value = [
        Writer(
            file_path=None,
            name="Leigh Brackett",
            imdb_id="nm0102824",
            titles=[
                Title(imdb_id="tt0038355", year=1946, title="The Big Sleep"),
                Title(imdb_id="tt0053221", year=1959, title="Rio Bravo"),
            ],
        )
    ]

    expected = [
        (1, "tt0372784", None, None, None, "Nolan's Batman", "nolans-batman"),
        (2, "tt0468569", None, None, None, "Nolan's Batman", "nolans-batman"),
        (3, "tt1345836", None, None, None, "Nolan's Batman", "nolans-batman"),
        (4, "tt0048424", "nm0001452", None, None, None, "charles-laughton"),
        (5, "tt0050280", None, "nm0001088", None, None, "peter-cushing"),
        (6, "tt0051554", None, "nm0001088", None, None, "peter-cushing"),
        (7, "tt0038355", None, None, "nm0102824", None, "leigh-brackett"),
        (8, "tt0053221", None, None, "nm0102824", None, "leigh-brackett"),
    ]

    watchlist_titles_table.update()

    assert sql_query("SELECT * FROM 'watchlist_titles';") == expected


def test_calls_refresh_all_item_titles_for_each_person_type(
    person_refresh_all_item_titles_mock: MockerFixture,
) -> None:
    watchlist_titles_table.update()

    person_refresh_all_item_titles_mock.assert_has_calls(
        [
            person_refresh_all_item_titles_mock.call(),
            person_refresh_all_item_titles_mock.call(),
            person_refresh_all_item_titles_mock.call(),
        ]
    )
