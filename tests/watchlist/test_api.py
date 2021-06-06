from pytest_mock import MockerFixture

from movielog.watchlist import api as watchlist_api


def test_refresh_credits_refreshes_all_types(mocker: MockerFixture) -> None:
    directors_refresh_mock = mocker.patch(
        "movielog.watchlist.api.directors.refresh_movies"
    )
    performers_refresh_mock = mocker.patch(
        "movielog.watchlist.api.performers.refresh_movies"
    )
    writers_refresh_mock = mocker.patch("movielog.watchlist.api.writers.refresh_movies")

    watchlist_api.refresh_credits()

    directors_refresh_mock.assert_called_once()
    performers_refresh_mock.assert_called_once()
    writers_refresh_mock.assert_called_once()
