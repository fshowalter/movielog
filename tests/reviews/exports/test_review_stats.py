import json
import os
from datetime import date

import pytest

from movielog.reviews import serializer
from movielog.reviews.exports import review_stats
from movielog.reviews.review import Review


@pytest.fixture(autouse=True)
def init_db() -> None:
    serializer.serialize(
        Review(
            slug="kill-bill-the-whole-bloody-affair-2011",
            imdb_id="tt6019206",
            grade="A",
            date=date(2016, 3, 12),
            review_content="Four words of content.",
        )
    )

    serializer.serialize(
        Review(
            slug="rio-bravo-1959",
            imdb_id="tt6019206",
            grade="A+",
            date=date(2017, 4, 10),
            review_content="Ten short words to make longer content for the average.",
        )
    )

    serializer.serialize(
        Review(
            slug="fright-night-1985",
            imdb_id="tt6019206",
            grade="A+",
            date=date(2017, 10, 31),
            review_content="Twelve words to make even longer content to pad out the average.",
        )
    )


def test_exports_review_stats(tmp_path: str) -> None:
    review_stats.export()

    expected = {
        "reviewYear": "2016",
        "reviewsCreated": 1,
    }

    with open(os.path.join(tmp_path, "review_stats", "2016.json"), "r") as file2016:
        file_content = json.load(file2016)

    assert file_content == expected

    expected = {
        "reviewYear": "2017",
        "reviewsCreated": 2,
    }

    with open(os.path.join(tmp_path, "review_stats", "2017.json"), "r") as file2017:
        file_content = json.load(file2017)

    assert file_content == expected

    expected = {
        "reviewYear": "all",
        "reviewsCreated": 3,
    }

    with open(os.path.join(tmp_path, "review_stats", "all.json"), "r") as file_all:
        file_content = json.load(file_all)

    assert file_content == expected
