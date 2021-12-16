import json
import os
from datetime import date

import pytest

from movielog.moviedata.core import movies_table
from movielog.reviews import reviews_table
from movielog.reviews.exports import average_grade_for_decades


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
                principal_cast_ids="",
                votes=32,
                imdb_rating=7.4,
            ),
            movies_table.Row(
                imdb_id="tt0051554",
                title="Horror of Dracula",
                original_title="Dracula",
                year=1958,
                runtime_minutes=111,
                principal_cast_ids="",
                votes=31,
                imdb_rating=6,
            ),
            movies_table.Row(
                imdb_id="tt0053220",
                title="Ride Lonesome",
                original_title="Ride Lonesome",
                year=1959,
                runtime_minutes=99,
                principal_cast_ids="",
                votes=16,
                imdb_rating=7.1,
            ),
            movies_table.Row(
                imdb_id="tt0087298",
                title="Friday the 13th: The Final Chapter (1984)",
                original_title="Friday the 13th: The Final Chapter (1984)",
                year=1984,
                runtime_minutes=92,
                principal_cast_ids="",
                votes=19,
                imdb_rating=4.5,
            ),
            movies_table.Row(
                imdb_id="tt0089175",
                title="Fright Night",
                original_title="Fright Night",
                year=1985,
                runtime_minutes=95,
                principal_cast_ids="",
                votes=18,
                imdb_rating=6.4,
            ),
        ]
    )

    reviews_table.reload(
        [
            reviews_table.Row(
                sequence=1,
                slug="ride-lonesome-1959",
                movie_imdb_id="tt0053220",
                grade="B",
                grade_value=4,
                venue="Vudu",
                date=date(2016, 3, 12),
            ),
            reviews_table.Row(
                sequence=2,
                slug="rio-bravo-1959",
                movie_imdb_id="tt0053221",
                grade="A+",
                grade_value=5.33,
                venue="Blu-ray",
                date=date(2016, 4, 10),
            ),
            reviews_table.Row(
                sequence=3,
                slug="fright-night-1985",
                movie_imdb_id="tt0089175",
                grade="A+",
                grade_value=5.33,
                venue="Blu-ray",
                date=date(2016, 10, 31),
            ),
            reviews_table.Row(
                sequence=1,
                slug="friday-the-13th-the-final-chapter-1984",
                movie_imdb_id="tt0087298",
                grade="B",
                grade_value=4,
                venue="Vudu",
                date=date(2017, 3, 12),
            ),
            reviews_table.Row(
                sequence=2,
                slug="horror-of-dracula-1958",
                movie_imdb_id="tt0051554",
                grade="A",
                grade_value=5,
                venue="Blu-ray",
                date=date(2017, 4, 10),
            ),
        ]
    )


def test_exports_average_grade_for_decades(tmp_path: str) -> None:
    average_grade_for_decades.export()

    expected = {
        "review_year": "2016",
        "stats": [
            {
                "decade": "1950s",
                "average_grade_value": 4.665,
            },
            {
                "decade": "1980s",
                "average_grade_value": 5.33,
            },
        ],
    }

    with open(
        os.path.join(tmp_path, "average_grade_for_decades", "2016.json"), "r"
    ) as file2016:
        file_content = json.load(file2016)

    assert file_content == expected

    expected = {
        "review_year": "2017",
        "stats": [
            {
                "decade": "1950s",
                "average_grade_value": 5.0,
            },
            {
                "decade": "1980s",
                "average_grade_value": 4.0,
            },
        ],
    }

    with open(
        os.path.join(tmp_path, "average_grade_for_decades", "2017.json"), "r"
    ) as file2017:
        file_content = json.load(file2017)

    assert file_content == expected

    expected = {
        "review_year": "all",
        "stats": [
            {
                "decade": "1950s",
                "average_grade_value": 4.776666666666666,
            },
            {
                "decade": "1980s",
                "average_grade_value": 4.665,
            },
        ],
    }

    with open(
        os.path.join(tmp_path, "average_grade_for_decades", "all.json"), "r"
    ) as file_all:
        file_content = json.load(file_all)

    assert file_content == expected
