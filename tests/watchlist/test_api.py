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


def test_export_data_calls_watchlist_table_update_with_all_people_and_collections(
    mocker: MockerFixture,
) -> None:
    mocker.patch(
        "movielog.watchlist.filmography.filmography_for_person", return_value=[]
    )

    mocker.patch("movielog.watchlist.api.exports_api.export")

    watchlist_table_mock = mocker.patch("movielog.watchlist.api.watchlist_table.update")

    director = watchlist_api.add_director(imdb_id="nm0001328", name="Howard Hawks")
    performer = watchlist_api.add_performer(imdb_id="nm0000078", name="John Wayne")
    writer = watchlist_api.add_writer(imdb_id="nm0102824", name="Leigh Brackett")
    collection = watchlist_api.add_collection("Bond")

    watchlist_api.export_data()

    watchlist_table_mock.assert_called_once_with(
        [director, performer, writer], [collection]
    )
