import datetime
import json
import os

import pytest

from movielog.moviedata.core import aka_titles_table, movies_table, people_table
from movielog.moviedata.extended.tables import (
    countries_table,
    directing_credits_table,
    release_dates_table,
    sort_titles_table,
)
from movielog.reviews import reviews_table
from movielog.reviews.exports import reviewed_movies


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

    people_table.reload(
        [
            people_table.Row(
                imdb_id="nm0001328",
                full_name="Howard Hawks",
                known_for_title_ids="",
            ),
            people_table.Row(
                imdb_id="nm0000078",
                full_name="John Wayne",
                known_for_title_ids="",
            ),
            people_table.Row(
                imdb_id="nm0001509",
                full_name="Dean Martin",
                known_for_title_ids="",
            ),
            people_table.Row(
                imdb_id="nm0625699",
                full_name="Ricky Nelson",
                known_for_title_ids="",
            ),
            people_table.Row(
                imdb_id="nm0001141",
                full_name="Angie Dickinson",
                known_for_title_ids="",
            ),
        ]
    )

    aka_titles_table.reload(
        [
            aka_titles_table.Row(
                movie_imdb_id="tt0053221",
                sequence=36,
                title="Howard Hawks' Rio Bravo",
                region="US",
                language=None,
                is_original_title=False,
                attributes="complete title",
                types=None,
            ),
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

    countries_table.reload(
        [countries_table.Row(movie_imdb_id="tt0053221", country="United States")]
    )

    sort_titles_table.reload(
        [sort_titles_table.Row(movie_imdb_id="tt0053221", sort_title="Rio Bravo")]
    )

    directing_credits_table.reload(
        [
            directing_credits_table.Row(
                movie_imdb_id="tt0053221",
                person_imdb_id="nm0001328",
                sequence=0,
                notes="",
            )
        ]
    )

    reviews_table.reload(
        [
            reviews_table.Row(
                movie_imdb_id="tt0053221",
                date=datetime.date(2021, 1, 29),
                sequence=165,
                grade="A+",
                grade_value=5.33,
                slug="rio-bravo-1959",
                venue="Blu-ray",
            )
        ]
    )


def test_create_serializes_new_review(tmp_path: str) -> None:
    expected = [
        {
            "imdb_id": "tt0053221",
            "title": "Rio Bravo",
            "original_title": "Original Rio Bravo",
            "year": 1959,
            "review_date": "2021-01-29",
            "review_sequence": 165,
            "release_date": "1959-03-18",
            "last_review_grade": "A+",
            "last_review_grade_value": 5.33,
            "slug": "rio-bravo-1959",
            "sort_title": "Rio Bravo",
            "principal_cast_ids": "nm0000078,nm0001509,nm0625699,nm0001141",
            "runtime_minutes": 141,
            "directors": [
                {
                    "full_name": "Howard Hawks",
                }
            ],
            "principal_cast": [
                {
                    "full_name": "John Wayne",
                },
                {
                    "full_name": "Dean Martin",
                },
                {
                    "full_name": "Ricky Nelson",
                },
                {"full_name": "Angie Dickinson"},
            ],
            "countries": ["United States"],
            "aka_titles": ["Howard Hawks' Rio Bravo", "Original Rio Bravo"],
        }
    ]

    reviewed_movies.export()

    with open(os.path.join(tmp_path, "reviewed_movies.json"), "r") as output_file:
        file_content = json.load(output_file)

    assert file_content == expected
