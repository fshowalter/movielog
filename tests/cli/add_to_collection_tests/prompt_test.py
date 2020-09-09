from typing import Callable, List

import pytest
from pytest_mock import MockerFixture

from movielog import watchlist
from movielog.cli import add_to_collection
from movielog.watchlist_file import Title
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
            ("tt0080761", "Friday the 13th", 1980, [("nm0658133", "Betsy Palmer")]),
            ("tt0082418", "Friday the 13th Part 2", 1981, [("nm0824386", "Amy Steel")]),
            (
                "tt0083972",
                "Friday the 13th Part III",
                1982,
                [("nm0050676", "Terry Ballard")],
            ),
            ("tt0116671", "Jack Frost", 1997, [("nm0531924", "Scott MacDonald")]),
        ]
    )


@pytest.fixture(autouse=True)
def mock_collection_add_title(mocker: MockerFixture) -> MockerFixture:
    collection = Collection(
        name="Friday the 13th",
        titles=[
            Title(imdb_id="tt0080761", year=1980, title="Friday the 13th"),
            Title(imdb_id="tt0082418", year=1981, title="Friday the 13th Part 2"),
            Title(imdb_id="tt0083972", year=1982, title="Friday the 13th Part III"),
        ],
    )
    mocker.patch(
        "movielog.cli.add_to_collection.watchlist.all_collections",
        return_value=[collection],
    )
    mocker.patch.object(collection, "save")
    return mocker.patch.object(collection, "add_title")


def test_calls_add_title_on_collection(
    mock_input: PosixPipeInput, mock_collection_add_title: MockerFixture
) -> None:
    mock_input.send_text(
        f"{Down}{Enter}The Final Chapter{Enter}{Down}{Enter}y{Enter}"  # noqa: WPS221
    )  # noqa: WPS221
    add_to_collection.prompt()

    mock_collection_add_title.assert_called_once_with(
        imdb_id="tt0087298", title="Friday the 13th: The Final Chapter", year=1984
    )


def test_does_not_call_add_director_if_no_selection(
    mock_input: PosixPipeInput, mock_collection_add_title: MockerFixture
) -> None:
    mock_input.send_text(f"{Down}{Enter}{Escape}{Escape}{Enter}")  # noqa: WPS221
    add_to_collection.prompt()

    mock_collection_add_title.assert_not_called()
