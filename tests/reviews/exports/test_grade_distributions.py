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
                sequence=1,
                slug="kill-bill-the-whole-bloody-affair-2011",
                movie_imdb_id="tt6019206",
                grade="A",
                grade_value=5,
                venue="Alamo Drafthouse One Loudon",
                date=date(2016, 3, 12),
            ),
            reviews_table.Row(
                sequence=2,
                slug="rio-bravo-1959",
                movie_imdb_id="tt6019206",
                grade="A+",
                grade_value=5.33,
                venue="Blu-ray",
                date=date(2017, 4, 10),
            ),
            reviews_table.Row(
                sequence=3,
                slug="fright-night-1985",
                movie_imdb_id="tt6019206",
                grade="A+",
                grade_value=5.33,
                venue="Blu-ray",
                date=date(2017, 10, 31),
            ),
        ]
    )


def test_exports_grade_distributions(tmp_path: str) -> None:
    grade_distributions.export()

    expected = {
        "review_year": "2016",
        "total_review_count": 1,
        "distributions": [
            {
                "grade": "A",
                "grade_value": 5,
                "review_count": 1,
            }
        ],
    }

    with open(
        os.path.join(tmp_path, "grade_distributions", "2016.json"), "r"
    ) as file2016:
        file_content = json.load(file2016)

    assert file_content == expected

    expected = {
        "review_year": "2017",
        "total_review_count": 2,
        "distributions": [
            {
                "grade": "A+",
                "grade_value": 5.33,
                "review_count": 2,
            }
        ],
    }

    with open(
        os.path.join(tmp_path, "grade_distributions", "2017.json"), "r"
    ) as file2017:
        file_content = json.load(file2017)

    assert file_content == expected

    expected = {
        "review_year": "all",
        "total_review_count": 3,
        "distributions": [
            {
                "grade": "A+",
                "grade_value": 5.33,
                "review_count": 2,
            },
            {
                "grade": "A",
                "grade_value": 5,
                "review_count": 1,
            },
        ],
    }

    with open(
        os.path.join(tmp_path, "grade_distributions", "all.json"), "r"
    ) as file_all:
        file_content = json.load(file_all)

    assert file_content == expected
