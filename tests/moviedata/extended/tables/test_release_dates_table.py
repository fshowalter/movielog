from datetime import date
from typing import Callable

from movielog.moviedata.extended.movies import Movie
from movielog.moviedata.extended.tables import release_dates_table
from tests.conftest import QueryResult


def test_update_adds_release_dates(sql_query: Callable[[str], QueryResult]) -> None:
    expected = [
        {
            "movie_imdb_id": "tt0053221",
            "release_date": "1959-03-18",
            "notes": "(limited)",
        },
        {"movie_imdb_id": "tt0092106", "release_date": "1986-08-08", "notes": ""},
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
            genres=["Animation", "Action"],
            countries=["United States", "Japan"],
        ),
        Movie(
            imdb_id="tt0053221",
            sort_title="Rio Bravo (1959)",
            directors=[],
            writers=[],
            cast=[],
            release_date=date(1959, 3, 18),
            release_date_notes="(limited)",
            genres=["Western"],
            countries=["United States"],
        ),
    ]

    release_dates_table.update(movies)

    assert sql_query("select * from release_dates order by release_date") == expected
