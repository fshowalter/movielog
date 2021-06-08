from pytest_mock import MockerFixture

from movielog.watchlist import api as watchlist_api
from movielog.watchlist import movies, serializer
from movielog.watchlist.collections import Collection
from movielog.watchlist.directors import Director
from movielog.watchlist.performers import Performer
from movielog.watchlist.writers import Writer


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


def test_export_data_calls_update_table_with_all_people_and_collections(
    mocker: MockerFixture,
) -> None:
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


def test_movies_returns_all_people_and_collections_movies() -> None:

    serializer.serialize(
        Director(
            frozen=True,
            imdb_id="nm0001328",
            name="Howard Hawks",
            slug="howard-hawks",
            movies=[
                movies.Movie(
                    title="Rio Bravo", year=1959, imdb_id="tt0053221", notes=""
                )
            ],
        )
    )

    serializer.serialize(
        Writer(
            frozen=True,
            imdb_id="nm0102824",
            name="Leigh Brackett",
            slug="leigh-brackett",
            movies=[
                movies.Movie(
                    imdb_id="tt0038355", title="The Big Sleep", year=1946, notes=""
                )
            ],
        )
    )

    serializer.serialize(
        Performer(
            frozen=True,
            imdb_id="nm0000078",
            name="John Wayne",
            slug="john-wayne",
            movies=[
                movies.Movie(
                    title="Rio Bravo", year=1959, imdb_id="tt0053221", notes=""
                )
            ],
        )
    )

    serializer.serialize(
        Collection(
            name="Vampire Movies",
            slug="vampire-movies",
            movies=[
                movies.Movie(
                    imdb_id="tt0089175",
                    title="Fright Night",
                    year=1985,
                    notes="",
                )
            ],
        )
    )

    expected = [
        movies.Movie(title="Rio Bravo", year=1959, imdb_id="tt0053221", notes=""),
        movies.Movie(title="Rio Bravo", year=1959, imdb_id="tt0053221", notes=""),
        movies.Movie(imdb_id="tt0038355", title="The Big Sleep", year=1946, notes=""),
        movies.Movie(
            imdb_id="tt0089175",
            title="Fright Night",
            year=1985,
            notes="",
        ),
    ]

    assert expected == watchlist_api.movies()
