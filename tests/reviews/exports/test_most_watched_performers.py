from __future__ import annotations

import datetime
import json
import os

import pytest

from movielog.moviedata.core import movies_table, people_table
from movielog.moviedata.extended.tables import performing_credits_table
from movielog.reviews import reviews_table, viewings_table
from movielog.reviews.exports import most_watched_performers
from movielog.watchlist import watchlist_table


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
                votes=14,
                imdb_rating=8.1,
            ),
            movies_table.Row(
                imdb_id="tt0038355",
                title="The Big Sleep",
                original_title="The Big Sleep",
                year=1946,
                runtime_minutes=111,
                principal_cast_ids="",
                votes=16,
                imdb_rating=8.0,
            ),
            movies_table.Row(
                imdb_id="tt0031971",
                title="Stagecoach",
                original_title="Stagecoach",
                year=1939,
                runtime_minutes=94,
                principal_cast_ids="",
                votes=32,
                imdb_rating=7.5,
            ),
            movies_table.Row(
                imdb_id="tt0089175",
                title="Fright Night",
                original_title="Fright Night",
                year=1985,
                runtime_minutes=95,
                principal_cast_ids="",
                votes=24,
                imdb_rating=6.7,
            ),
        ]
    )

    people_table.reload(
        [
            people_table.Row(
                imdb_id="nm0000078",
                full_name="John Wayne",
                known_for_title_ids="",
            ),
            people_table.Row(
                imdb_id="nm0000007",
                full_name="Humphrey Bogart",
                known_for_title_ids="",
            ),
            people_table.Row(
                imdb_id="nm0001697",
                full_name="Chris Sarandon",
                known_for_title_ids="",
            ),
        ]
    )

    performing_credits_table.reload(
        [
            performing_credits_table.Row(
                movie_imdb_id="tt0053221",
                person_imdb_id="nm0000078",
                sequence=0,
                notes="",
            ),
            performing_credits_table.Row(
                movie_imdb_id="tt0038355",
                person_imdb_id="nm0000007",
                sequence=0,
                notes="",
            ),
            performing_credits_table.Row(
                movie_imdb_id="tt0031971",
                person_imdb_id="nm0000078",
                sequence=0,
                notes="",
            ),
            performing_credits_table.Row(
                movie_imdb_id="tt0089175",
                person_imdb_id="nm0001697",
                sequence=0,
                notes="",
            ),
        ]
    )

    viewings_table.reload(
        [
            viewings_table.Row(
                movie_imdb_id="tt0053221",
                date=datetime.date(2016, 6, 19),
                sequence=1,
                venue="Alamo Drafthouse",
            ),
            viewings_table.Row(
                movie_imdb_id="tt0038355",
                date=datetime.date(2017, 3, 12),
                sequence=2,
                venue="Blu-ray",
            ),
            viewings_table.Row(
                movie_imdb_id="tt0031971",
                date=datetime.date(2017, 4, 29),
                sequence=3,
                venue="New Beverly",
            ),
            viewings_table.Row(
                movie_imdb_id="tt0089175",
                date=datetime.date(2017, 10, 31),
                sequence=4,
                venue="AFI Silver",
            ),
        ]
    )

    reviews_table.reload(
        [
            reviews_table.Row(
                movie_imdb_id="tt0053221",
                date=datetime.date(2016, 6, 19),
                sequence=1,
                grade="A+",
                grade_value=5.33,
                slug="rio-bravo-1959",
                venue="Alamo Drafthouse",
            ),
            reviews_table.Row(
                movie_imdb_id="tt0038355",
                date=datetime.date(2017, 3, 12),
                sequence=2,
                grade="A",
                grade_value=5,
                slug="the-big-sleep-1946",
                venue="Blu-ray",
            ),
            reviews_table.Row(
                movie_imdb_id="tt0031971",
                date=datetime.date(2017, 4, 29),
                sequence=3,
                grade="A",
                grade_value=5,
                slug="stagecoach-1939",
                venue="New Beverly",
            ),
            reviews_table.Row(
                movie_imdb_id="tt0089175",
                date=datetime.date(2017, 10, 31),
                sequence=4,
                grade="A+",
                grade_value=5.33,
                slug="fright-night-1985",
                venue="AFI Silver",
            ),
        ]
    )

    watchlist_table.reload(
        [
            watchlist_table.Row(
                movie_imdb_id="tt0053221",
                director_imdb_id=None,
                slug="john-wayne",
                performer_imdb_id="nm0000078",
                writer_imdb_id=None,
                collection_name=None,
            ),
            watchlist_table.Row(
                movie_imdb_id="tt0038355",
                director_imdb_id=None,
                slug="humphrey-bogart",
                performer_imdb_id="nm0000007",
                writer_imdb_id=None,
                collection_name=None,
            ),
            watchlist_table.Row(
                movie_imdb_id="tt0031971",
                director_imdb_id=None,
                slug="john-wayne",
                performer_imdb_id="nm0000078",
                writer_imdb_id=None,
                collection_name=None,
            ),
        ]
    )


def test_exports_most_watched_performers(tmp_path: str) -> None:

    most_watched_performers.export()

    expected: dict[str, object] = {
        "viewing_year": "2016",
        "most_watched": [],
    }

    with open(
        os.path.join(tmp_path, "most_watched_performers", "2016.json"), "r"
    ) as file2016:
        file_content = json.load(file2016)

    assert file_content == expected

    expected = {
        "viewing_year": "2017",
        "most_watched": [],
    }

    with open(
        os.path.join(tmp_path, "most_watched_performers", "2017.json"), "r"
    ) as file2017:
        file_content = json.load(file2017)

    assert file_content == expected

    expected = {
        "viewing_year": "all",
        "most_watched": [
            {
                "imdb_id": "nm0000078",
                "full_name": "John Wayne",
                "slug": "john-wayne",
                "viewing_count": 2,
                "viewings": [
                    {
                        "sequence": 1,
                        "venue": "Alamo Drafthouse",
                        "date": "2016-06-19",
                        "title": "Rio Bravo",
                        "year": 1959,
                        "slug": "rio-bravo-1959",
                        "imdb_id": "tt0053221",
                    },
                    {
                        "sequence": 3,
                        "venue": "New Beverly",
                        "date": "2017-04-29",
                        "title": "Stagecoach",
                        "year": 1939,
                        "slug": "stagecoach-1939",
                        "imdb_id": "tt0031971",
                    },
                ],
            },
        ],
    }

    with open(
        os.path.join(tmp_path, "most_watched_performers", "all.json"), "r"
    ) as file_all:
        file_content = json.load(file_all)

    assert file_content == expected
