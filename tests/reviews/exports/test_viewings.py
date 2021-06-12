import datetime
import json
import os

import pytest

from movielog.moviedata.core import movies_table
from movielog.moviedata.extended.tables import release_dates_table, sort_titles_table
from movielog.reviews import viewings_table
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
            )
        ]
    )

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

    viewings_table.reload(
        [
            viewings_table.Row(
                movie_imdb_id="tt0053221",
                date=datetime.date(2021, 1, 29),
                sequence=165,
                venue="Blu-ray",
            )
        ]
    )


def test_exports_viewings(tmp_path: str) -> None:
    expected = [
        {
            "imdb_id": "tt0053221",
            "title": "Rio Bravo",
            "year": 1959,
            "viewing_date": "2021-01-29",
            "sequence": 165,
            "viewing_year": "2021",
            "release_date": "1959-03-18",
            "sort_title": "Rio Bravo",
            "venue": "Blu-ray",
        }
    ]

    viewings.export()

    with open(os.path.join(tmp_path, "viewings.json"), "r") as output_file:
        file_content = json.load(output_file)

    assert file_content == expected
