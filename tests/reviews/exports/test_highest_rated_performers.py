import datetime
import json
import os

import pytest

from movielog.moviedata.core import movies_table, people_table
from movielog.moviedata.extended.tables import performing_credits_table
from movielog.reviews import reviews_table
from movielog.reviews.exports import highest_rated_performers
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
                votes=32,
                imdb_rating=8.1,
            ),
            movies_table.Row(
                imdb_id="tt0038355",
                title="The Big Sleep",
                original_title="The Big Sleep",
                year=1946,
                runtime_minutes=111,
                principal_cast_ids="",
                votes=23,
                imdb_rating=7.9,
            ),
            movies_table.Row(
                imdb_id="tt0031971",
                title="Stagecoach",
                original_title="Stagecoach",
                year=1939,
                runtime_minutes=96,
                principal_cast_ids="",
                votes=23,
                imdb_rating=7.7,
            ),
            movies_table.Row(
                imdb_id="tt0089175",
                title="Fright Night",
                original_title="Fright Night",
                year=1985,
                runtime_minutes=95,
                principal_cast_ids="",
                votes=16,
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


def test_exports_highest_rated_performers(tmp_path: str) -> None:

    highest_rated_performers.export()

    expected = {
        "review_year": "2016",
        "highest_rated": [
            {
                "imdb_id": "nm0000078",
                "full_name": "John Wayne",
                "slug": "john-wayne",
                "average_grade_value": 5.33,
                "review_count": 1,
                "reviews": [
                    {
                        "sequence": 1,
                        "grade_value": 5.33,
                        "date": "2016-06-19",
                        "title": "Rio Bravo",
                        "year": 1959,
                        "slug": "rio-bravo-1959",
                    }
                ],
            },
        ],
    }

    with open(
        os.path.join(tmp_path, "highest_rated_performers", "2016.json"), "r"
    ) as file2016:
        file_content = json.load(file2016)

    assert file_content == expected

    expected = {
        "review_year": "2017",
        "highest_rated": [
            {
                "imdb_id": "nm0001697",
                "full_name": "Chris Sarandon",
                "slug": None,
                "average_grade_value": 5.33,
                "review_count": 1,
                "reviews": [
                    {
                        "sequence": 4,
                        "grade_value": 5.33,
                        "date": "2017-10-31",
                        "title": "Fright Night",
                        "year": 1985,
                        "slug": "fright-night-1985",
                    }
                ],
            },
            {
                "imdb_id": "nm0000007",
                "full_name": "Humphrey Bogart",
                "slug": "humphrey-bogart",
                "average_grade_value": 5.0,
                "review_count": 1,
                "reviews": [
                    {
                        "sequence": 2,
                        "grade_value": 5,
                        "date": "2017-03-12",
                        "title": "The Big Sleep",
                        "year": 1946,
                        "slug": "the-big-sleep-1946",
                    }
                ],
            },
            {
                "imdb_id": "nm0000078",
                "full_name": "John Wayne",
                "slug": "john-wayne",
                "average_grade_value": 5.0,
                "review_count": 1,
                "reviews": [
                    {
                        "sequence": 3,
                        "grade_value": 5,
                        "date": "2017-04-29",
                        "title": "Stagecoach",
                        "year": 1939,
                        "slug": "stagecoach-1939",
                    }
                ],
            },
        ],
    }

    with open(
        os.path.join(tmp_path, "highest_rated_performers", "2017.json"), "r"
    ) as file2017:
        file_content = json.load(file2017)

    assert file_content == expected

    expected = {
        "review_year": "all",
        "highest_rated": [
            {
                "imdb_id": "nm0001697",
                "full_name": "Chris Sarandon",
                "slug": None,
                "average_grade_value": 5.33,
                "review_count": 1,
                "reviews": [
                    {
                        "sequence": 4,
                        "grade_value": 5.33,
                        "date": "2017-10-31",
                        "title": "Fright Night",
                        "year": 1985,
                        "slug": "fright-night-1985",
                    }
                ],
            },
            {
                "imdb_id": "nm0000078",
                "full_name": "John Wayne",
                "slug": "john-wayne",
                "average_grade_value": 5.165,
                "review_count": 2,
                "reviews": [
                    {
                        "sequence": 1,
                        "grade_value": 5.33,
                        "date": "2016-06-19",
                        "title": "Rio Bravo",
                        "year": 1959,
                        "slug": "rio-bravo-1959",
                    },
                    {
                        "sequence": 3,
                        "grade_value": 5,
                        "date": "2017-04-29",
                        "title": "Stagecoach",
                        "year": 1939,
                        "slug": "stagecoach-1939",
                    },
                ],
            },
            {
                "imdb_id": "nm0000007",
                "full_name": "Humphrey Bogart",
                "slug": "humphrey-bogart",
                "average_grade_value": 5.0,
                "review_count": 1,
                "reviews": [
                    {
                        "sequence": 2,
                        "grade_value": 5,
                        "date": "2017-03-12",
                        "title": "The Big Sleep",
                        "year": 1946,
                        "slug": "the-big-sleep-1946",
                    },
                ],
            },
        ],
    }

    with open(
        os.path.join(tmp_path, "highest_rated_performers", "all.json"), "r"
    ) as file_all:
        file_content = json.load(file_all)

    assert file_content == expected
