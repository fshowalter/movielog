from datetime import date
from typing import Callable

from movielog.moviedata.extended.movies import Movie
from movielog.moviedata.extended.tables import sort_titles_table
from tests.conftest import QueryResult


def test_update_adds_sort_titles(sql_query: Callable[[str], QueryResult]) -> None:
    expected = [
        {
            "movie_imdb_id": "tt0053221",
            "sort_title": "Rio Bravo (1959)",
        },
        {"movie_imdb_id": "tt0092106", "sort_title": "Transformers: The Movie (1986)"},
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

    sort_titles_table.update(movies)

    assert sql_query("select * from sort_titles order by movie_imdb_id") == expected
