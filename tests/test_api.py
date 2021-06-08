from datetime import date
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog import api as movielog_api
from movielog.viewings.viewing import Viewing
from movielog.watchlist.movies import Movie


@pytest.fixture(autouse=True)
def reviews_export_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.api.reviews_api.export_data")


@pytest.fixture(autouse=True)
def viewings_export_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.api.viewings_api.export_data")


@pytest.fixture(autouse=True)
def watchlist_export_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.api.watchlist_api.export_data")


@pytest.fixture(autouse=True)
def update_extended_data_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.api.moviedata_api.update_extended_data")


@pytest.fixture(autouse=True)
def mock_viewings(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "movielog.api.viewings_api.viewings",
        return_value=[
            Viewing(
                sequence=1,
                date=date(2016, 3, 12),
                imdb_id="tt0053221",
                title="Rio Bravo",
                venue="Blu-ray",
            ),
            Viewing(
                sequence=2,
                date=date(2017, 3, 12),
                imdb_id="tt0038355",
                title="The Big Sleep",
                venue="Blu-ray",
            ),
            Viewing(
                sequence=3,
                date=date(2018, 3, 12),
                imdb_id="tt0089175",
                title="Fright Night",
                venue="Blu-ray",
            ),
        ],
    )


@pytest.fixture(autouse=True)
def mock_watchlist_movies(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "movielog.api.watchlist_api.movies",
        return_value=[
            Movie(
                imdb_id="tt0053221",
                title="Rio Bravo",
                year=1959,
            ),
            Movie(
                imdb_id="tt0038355",
                title="The Big Sleep",
                year=1946,
            ),
            Movie(
                imdb_id="tt0031971",
                title="Stagecoach",
                year=1939,
            ),
        ],
    )


def test_export_data_calls_update_extended_data_with_viewing_and_watchlist_imdb_ids(
    update_extended_data_mock: MagicMock,
) -> None:
    movielog_api.export_data()

    update_extended_data_mock.assert_called_once_with(
        set(["tt0053221", "tt0038355", "tt0089175", "tt0031971"])
    )


def test_export_data_calls_export_date_for_reviews(
    reviews_export_mock: MagicMock,
) -> None:
    movielog_api.export_data()

    reviews_export_mock.assert_called_once()


def test_export_data_calls_export_date_for_viewings(
    viewings_export_mock: MagicMock,
) -> None:
    movielog_api.export_data()

    viewings_export_mock.assert_called_once()


def test_export_data_calls_export_date_for_watchlist(
    watchlist_export_mock: MagicMock,
) -> None:
    movielog_api.export_data()

    watchlist_export_mock.assert_called_once()
