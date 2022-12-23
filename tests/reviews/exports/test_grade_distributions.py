import json
import os
from datetime import date

import pytest

from movielog.reviews import reviews_table
from movielog.reviews.exports import grade_distributions


@pytest.fixture(autouse=True)
def init_db() -> None:
    reviews_table.reload(
        [
            reviews_table.Row(
                slug="kill-bill-the-whole-bloody-affair-2011",
                movie_imdb_id="tt6019206",
                grade="A",
                grade_value=5,
                date=date(2016, 3, 12),
            ),
            reviews_table.Row(
                slug="rio-bravo-1959",
                movie_imdb_id="tt6019206",
                grade="A+",
                grade_value=6,
                date=date(2017, 4, 10),
            ),
            reviews_table.Row(
                slug="fright-night-1985",
                movie_imdb_id="tt6019206",
                grade="A+",
                grade_value=6,
                date=date(2017, 10, 31),
            ),
        ]
    )


def test_exports_grade_distributions(tmp_path: str) -> None:
    grade_distributions.export()

    expected = [
        {
            "grade": "A+",
            "gradeValue": 6,
            "reviewCount": 2,
        },
        {
            "grade": "A",
            "gradeValue": 5,
            "reviewCount": 1,
        },
    ]

    with open(os.path.join(tmp_path, "grade_distributions.json"), "r") as file_all:
        file_content = json.load(file_all)

    assert file_content == expected
