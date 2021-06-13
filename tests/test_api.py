from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog import api as movielog_api


@pytest.fixture(autouse=True)
def reviews_export_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.api.reviews_api.export_data")


@pytest.fixture(autouse=True)
def watchlist_export_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.api.watchlist_api.export_data")


@pytest.fixture(autouse=True)
def update_extended_data_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.api.moviedata_api.update_extended_data")


@pytest.fixture(autouse=True)
def mock_review_movie_ids(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "movielog.api.reviews_api.movie_ids",
        return_value=set(["tt0053221", "tt0038355", "tt0089175"]),
    )


@pytest.fixture(autouse=True)
def mock_watchlist_movie_ids(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "movielog.api.watchlist_api.movie_ids",
        return_value=set(["tt0053221", "tt0038355", "tt0031971"]),
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


def test_export_data_calls_export_date_for_watchlist(
    watchlist_export_mock: MagicMock,
) -> None:
    movielog_api.export_data()

    watchlist_export_mock.assert_called_once()
