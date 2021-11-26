from datetime import date
from typing import Callable

from movielog.moviedata.extended.cast import Credit
from movielog.moviedata.extended.movies import Movie
from movielog.moviedata.extended.tables import performing_credits_table
from tests.conftest import QueryResult


def test_update_adds_performers(sql_query: Callable[[str], QueryResult]) -> None:
    expected = [
        {
            "movie_imdb_id": "tt0053221",
            "person_imdb_id": "nm0000078",
            "sequence": 0,
            "notes": "",
        },
        {
            "movie_imdb_id": "tt0053221",
            "person_imdb_id": "nm0001509",
            "sequence": 1,
            "notes": "('Borrachón')",
        },
    ]

    movies = [
        Movie(
            imdb_id="tt0053221",
            sort_title="Rio Bravo (1959)",
            directors=[],
            writers=[],
            cast=[
                Credit(
                    person_imdb_id="nm0000078",
                    name="John Wayne",
                    sequence=0,
                    notes="",
                    roles=["Sheriff John T. Chance"],
                ),
                Credit(
                    person_imdb_id="nm0001509",
                    name="Dean Margin",
                    sequence=1,
                    notes="('Borrachón')",
                    roles=["Dude"],
                ),
            ],
            genres=["Western"],
            release_date=date(1959, 3, 18),
            release_date_notes="",
            countries=["United States"],
        )
    ]

    performing_credits_table.update(movies)

    assert (
        sql_query("select * from performing_credits order by movie_imdb_id, sequence")
        == expected
    )
