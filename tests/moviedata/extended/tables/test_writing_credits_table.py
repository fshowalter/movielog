from datetime import date
from typing import Callable

from movielog.moviedata.extended.movies import Movie
from movielog.moviedata.extended.tables import writing_credits_table
from movielog.moviedata.extended.writers import Credit
from tests.conftest import QueryResult


def test_update_adds_writers(sql_query: Callable[[str], QueryResult]) -> None:
    expected = [
        {
            "movie_imdb_id": "tt0477348",
            "person_imdb_id": "nm0001054",
            "sequence": 0,
            "group_id": 0,
            "notes": "(screenplay)",
        },
        {
            "movie_imdb_id": "tt0477348",
            "person_imdb_id": "nm0001053",
            "sequence": 1,
            "group_id": 0,
            "notes": "(screenplay)",
        },
        {
            "movie_imdb_id": "tt0477348",
            "person_imdb_id": "nm0565092",
            "sequence": 0,
            "group_id": 1,
            "notes": "(novel)",
        },
    ]

    movies = [
        Movie(
            imdb_id="tt0477348",
            sort_title="No Country for Old Men (2007)",
            directors=[],
            writers=[
                Credit(
                    person_imdb_id="nm0001054",
                    name="Joel Coen",
                    group=0,
                    sequence=0,
                    notes="(screenplay)",
                ),
                Credit(
                    person_imdb_id="nm0001053",
                    name="Ethan Coen",
                    sequence=1,
                    group=0,
                    notes="(screenplay)",
                ),
                Credit(
                    person_imdb_id="nm0565092",
                    name="Cormac McCarthy",
                    group=1,
                    sequence=0,
                    notes="(novel)",
                ),
            ],
            cast=[],
            release_date=date(1984, 8, 8),
            release_date_notes="",
            genres=["Crime", "Drama"],
            countries=["United States"],
        )
    ]

    writing_credits_table.update(movies)

    assert (
        sql_query(
            "select * from writing_credits order by movie_imdb_id, group_id, sequence"
        )
        == expected
    )
