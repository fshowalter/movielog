from datetime import date
from typing import Callable

from movielog.moviedata.extended.directors import Credit
from movielog.moviedata.extended.movies import Movie
from movielog.moviedata.extended.tables import directing_credits_table
from tests.conftest import QueryResult


def test_update_adds_directors(sql_query: Callable[[str], QueryResult]) -> None:
    expected = [
        {
            "movie_imdb_id": "tt0086979",
            "person_imdb_id": "nm0001054",
            "sequence": 0,
            "notes": "",
        },
        {
            "movie_imdb_id": "tt0086979",
            "person_imdb_id": "nm0001053",
            "sequence": 1,
            "notes": "(uncredited)",
        },
    ]

    movies = [
        Movie(
            imdb_id="tt0086979",
            sort_title="Blood Simple (1984)",
            directors=[
                Credit(
                    person_imdb_id="nm0001054", name="Joel Coen", sequence=0, notes=""
                ),
                Credit(
                    person_imdb_id="nm0001053",
                    name="Ethan Coen",
                    sequence=1,
                    notes="(uncredited)",
                ),
            ],
            writers=[],
            cast=[],
            genres=["Crime", "Drama"],
            release_date=date(1984, 8, 8),
            release_date_notes="",
            countries=["United States"],
        )
    ]

    directing_credits_table.update(movies)

    assert (
        sql_query("select * from directing_credits order by movie_imdb_id, sequence")
        == expected
    )
