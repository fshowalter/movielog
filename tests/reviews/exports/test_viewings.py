import datetime
import json
import os

import pytest

from movielog.moviedata.core import movies_table
from movielog.moviedata.extended.tables import (
    genres_table,
    release_dates_table,
    sort_titles_table,
)
from movielog.reviews import api as reviews_api
from movielog.reviews import reviews_table, viewings_table
from movielog.reviews.exports import viewings


@pytest.fixture(autouse=True)
def init_db() -> None:
    movies_table.reload(
        [
            movies_table.Row(
                imdb_id="tt0053221",
                title="Rio Bravo",
                original_title="Original Rio Bravo",
                year=1959,
                runtime_minutes=141,
                principal_cast_ids="nm0000078,nm0001509,nm0625699,nm0001141",
                votes=8,
                imdb_rating=6.1,
            )
        ]
    )

    genres_table.reload([genres_table.Row(movie_imdb_id="tt0053221", genre="Western")])

    release_dates_table.reload(
        [
            release_dates_table.Row(
                movie_imdb_id="tt0053221",
                release_date=datetime.date(1959, 3, 18),
                notes="",
            )
        ]
    )

    sort_titles_table.reload(
        [sort_titles_table.Row(movie_imdb_id="tt0053221", sort_title="Rio Bravo")]
    )

    review = reviews_api.create(
        datetime.date(2021, 1, 29),
        imdb_id="tt0053221",
        title="Rio Bravo",
        year=1959,
        grade="A+",
        venue="Blu-ray",
    )

    reviews_table.update([review])
    viewings_table.update([review])


def test_exports_viewings(tmp_path: str) -> None:
    expected = [
        {
            "imdb_id": "tt0053221",
            "title": "Rio Bravo",
            "year": 1959,
            "viewing_date": "2021-01-29",
            "sequence": 1,
            "genres": ["Western"],
            "viewing_year": "2021",
            "release_date": "1959-03-18",
            "sort_title": "Rio Bravo",
            "venue": "Blu-ray",
            "slug": "rio-bravo-1959",
            "grade": "A+",
        }
    ]

    viewings.export()

    with open(os.path.join(tmp_path, "viewings.json"), "r") as output_file:
        file_content = json.load(output_file)

    assert file_content == expected
