from typing import Callable, List

import pytest
from pytest_mock import MockFixture

from movielog import watchlist
from movielog.cli import add_to_collection
from tests.cli.keys import Down, Enter, Escape
from tests.cli.typehints import MovieTuple, PosixPipeInput

Collection = watchlist.Collection


@pytest.fixture(autouse=True)
def seed_db(seed_movies: Callable[[List[MovieTuple]], None]) -> None:
    seed_movies(
        [
            ("tt0051554", "Horror of Dracula", 1958, [("nm0001088", "Peter Cushing")]),
            (
                "tt0087298",
                "Friday the 13th: The Final Chapter",
                1984,
                [("nm0000397", "Corey Feldman")],
            ),
            ("tt0089175", "Fright Night", 1985, [("nm0001697", "Chris Sarandon")]),
            ("tt0116671", "Jack Frost", 1997, [("nm0531924", "Scott MacDonald")]),
        ]
    )


@pytest.fixture(autouse=True)
def mock_collection_add_title(mocker: MockFixture) -> MockFixture:
    collection = Collection(name="Friday the 13th")
    mocker.patch(
        "movielog.cli.add_to_collection.watchlist.all_collections",
        return_value=[collection],
    )
    return mocker.patch.object(collection, "add_title")


def test_calls_add_title_on_collection(
    mock_input: PosixPipeInput, mock_collection_add_title: MockFixture
) -> None:
    mock_input.send_text(
        f"{Down}{Enter}Friday the 13th{Enter}{Down}{Enter}y{Enter}"
    )  # noqa: WPS221
    add_to_collection.prompt()

    mock_collection_add_title.assert_called_once_with(
        imdb_id="tt0087298", title="Friday the 13th: The Final Chapter", year=1984
    )


def test_does_not_call_add_director_if_no_selection(
    mock_input: PosixPipeInput, mock_collection_add_title: MockFixture
) -> None:
    mock_input.send_text(f"{Down}{Enter}{Escape}{Escape}{Enter}")  # noqa: WPS221
    add_to_collection.prompt()

    mock_collection_add_title.assert_not_called()
