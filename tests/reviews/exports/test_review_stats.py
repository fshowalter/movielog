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
            sequence=1,
            slug="kill-bill-the-whole-bloody-affair-2011",
            imdb_id="tt6019206",
            title="Kill Bill: The Whole Bloody Affair (2011)",
            grade="A",
            venue="Alamo Drafthouse One Loudon",
            date=date(2016, 3, 12),
            review_content="Four words of content.",
        )
    )

    serializer.serialize(
        Review(
            sequence=2,
            slug="rio-bravo-1959",
            imdb_id="tt6019206",
            title="Rio Bravo (1959)",
            grade="A+",
            venue="Blu-ray",
            date=date(2017, 4, 10),
            review_content="Ten short words to make longer content for the average.",
        )
    )

    serializer.serialize(
        Review(
            sequence=3,
            slug="fright-night-1985",
            imdb_id="tt6019206",
            title="Fright Night (1985)",
            grade="A+",
            venue="Blu-ray",
            date=date(2017, 10, 31),
            review_content="Twelve words to make even longer content to pad out the average.",
        )
    )


def test_exports_review_stats(tmp_path: str) -> None:
    review_stats.export()

    expected = {
        "review_year": "2016",
        "total_review_count": 1,
        "average_words_per_review": 4,
    }

    with open(os.path.join(tmp_path, "review_stats", "2016.json"), "r") as file2016:
        file_content = json.load(file2016)

    assert file_content == expected

    expected = {
        "review_year": "2017",
        "total_review_count": 2,
        "average_words_per_review": 11,
    }

    with open(os.path.join(tmp_path, "review_stats", "2017.json"), "r") as file2017:
        file_content = json.load(file2017)

    assert file_content == expected

    expected = {
        "review_year": "all",
        "total_review_count": 3,
        "average_words_per_review": 8.666666666666666,
    }

    with open(os.path.join(tmp_path, "review_stats", "all.json"), "r") as file_all:
        file_content = json.load(file_all)

    assert file_content == expected
