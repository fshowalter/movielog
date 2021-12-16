import datetime
import json
import os

import pytest

from movielog.moviedata.core import movies_table
from movielog.reviews import reviews_table, viewings_table
from movielog.reviews.exports import most_watched_movies


@pytest.fixture(autouse=True)
def init_db() -> None:
    movies_table.reload(
        [
            movies_table.Row(
                imdb_id="tt0053221",
                title="Rio Bravo",
                original_title="Rio Bravo",
                year=1959,
                runtime_minutes=141,
                principal_cast_ids="nm0000078",
                votes=32,
                imdb_rating=8.1,
            ),
            movies_table.Row(
                imdb_id="tt0190590",
                title="O Brother, Where Art Thou?",
                original_title="O Brother, Where Art Thou?",
                year=2000,
                runtime_minutes=121,
                principal_cast_ids="",
                votes=16,
                imdb_rating=6.7,
            ),
        ]
    )

    reviews_table.reload(
        [
            reviews_table.Row(
                movie_imdb_id="tt0053221",
                date=datetime.date(2021, 1, 29),
                sequence=3,
                grade="A+",
                grade_value=5.33,
                slug="rio-bravo-1959",
                venue="Blu-ray",
            )
        ]
    )

    viewings_table.reload(
        [
            viewings_table.Row(
                movie_imdb_id="tt0053221",
                date=datetime.date(2017, 3, 12),
                sequence=1,
                venue="AFI Silver",
            ),
            viewings_table.Row(
                movie_imdb_id="tt0053221",
                date=datetime.date(2017, 6, 19),
                sequence=2,
                venue="Alamo Drafthouse",
            ),
            viewings_table.Row(
                movie_imdb_id="tt0053221",
                date=datetime.date(2021, 1, 29),
                sequence=3,
                venue="Blu-ray",
            ),
            viewings_table.Row(
                movie_imdb_id="tt0190590",
                date=datetime.date(2021, 4, 12),
                sequence=4,
                venue="Blu-ray",
            ),
        ]
    )


def test_exports_most_watched_movies(tmp_path: str) -> None:
    most_watched_movies.export()

    expected = {
        "viewing_year": "2017",
        "most_watched": [
            {
                "imdb_id": "tt0053221",
                "title": "Rio Bravo",
                "year": 1959,
                "viewing_count": 2,
                "viewings": [
                    {
                        "date": "2017-03-12",
                        "venue": "AFI Silver",
                        "slug": None,
                        "sequence": 1,
                    },
                    {
                        "date": "2017-06-19",
                        "venue": "Alamo Drafthouse",
                        "slug": None,
                        "sequence": 2,
                    },
                ],
            },
        ],
    }

    with open(
        os.path.join(tmp_path, "most_watched_movies", "2017.json"), "r"
    ) as output_file2017:
        file_content = json.load(output_file2017)

    assert file_content == expected

    expected = {
        "viewing_year": "2021",
        "most_watched": [],
    }

    with open(
        os.path.join(tmp_path, "most_watched_movies", "2021.json"), "r"
    ) as output_file2021:
        file_content = json.load(output_file2021)

    assert file_content == expected

    expected = {
        "viewing_year": "all",
        "most_watched": [
            {
                "imdb_id": "tt0053221",
                "title": "Rio Bravo",
                "year": 1959,
                "viewing_count": 3,
                "viewings": [
                    {
                        "date": "2017-03-12",
                        "venue": "AFI Silver",
                        "slug": None,
                        "sequence": 1,
                    },
                    {
                        "date": "2017-06-19",
                        "venue": "Alamo Drafthouse",
                        "slug": None,
                        "sequence": 2,
                    },
                    {
                        "date": "2021-01-29",
                        "venue": "Blu-ray",
                        "slug": "rio-bravo-1959",
                        "sequence": 3,
                    },
                ],
            },
        ],
    }

    with open(
        os.path.join(tmp_path, "most_watched_movies", "all.json"), "r"
    ) as output_file_all:
        file_content = json.load(output_file_all)

    assert file_content == expected
