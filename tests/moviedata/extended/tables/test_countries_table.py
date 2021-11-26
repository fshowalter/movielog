from datetime import date
from typing import Callable

from movielog.moviedata.extended.movies import Movie
from movielog.moviedata.extended.tables import countries_table
from tests.conftest import QueryResult


def test_update_adds_countries(sql_query: Callable[[str], QueryResult]) -> None:
    expected = [
        {"movie_imdb_id": "tt0092106", "country": "Japan"},
        {"movie_imdb_id": "tt0092106", "country": "United States"},
    ]

    movies = [
        Movie(
            imdb_id="tt0092106",
            sort_title="Transformers: The Movie (1986)",
            directors=[],
            writers=[],
            cast=[],
            release_date=date(1986, 8, 8),
            release_date_notes="",
            countries=["United States", "Japan"],
            genres=["Animation", "Action"],
        )
    ]

    countries_table.update(movies)

    assert sql_query("select * from countries order by country") == expected
