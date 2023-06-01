import datetime
import json
import os

import pytest

from movielog.moviedata.core import aka_titles_table, movies_table, people_table
from movielog.moviedata.extended.tables import (
    countries_table,
    directing_credits_table,
    genres_table,
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
                original_title="Rio Bravo",
                year=1959,
                runtime_minutes=141,
                principal_cast_ids="nm0000078,nm0001509,nm0625699",
                votes=20,
                imdb_rating=8.1,
            ),
            movies_table.Row(
                imdb_id="tt0051554",
                title="Horror of Dracula",
                original_title="Dracula",
                year=1958,
                runtime_minutes=98,
                principal_cast_ids="nm0001088,nm0000489",
                votes=18,
                imdb_rating=6.7,
            ),
            movies_table.Row(
                imdb_id="tt0098327",
                title="The Seventh Continent",
                original_title="Der siebente Kontinent",
                year=1989,
                runtime_minutes=120,
                principal_cast_ids="",
                votes=17,
                imdb_rating=7.4,
            ),
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
                imdb_id="nm0001088",
                full_name="Peter Cushing",
                known_for_title_ids="",
            ),
            people_table.Row(
                imdb_id="nm0000489",
                full_name="Christopher Lee",
                known_for_title_ids="",
            ),
            people_table.Row(
                imdb_id="nm0279807",
                full_name="Terence Fisher",
                known_for_title_ids="",
            ),
            people_table.Row(
                imdb_id="nm0359734",
                full_name="Michael Haneke",
                known_for_title_ids="",
            ),
        ]
    )

    aka_titles_table.reload(
        [
            aka_titles_table.Row(
                movie_imdb_id="tt0053221",
                sequence=1,
                title="Howard Hawks' Rio Bravo",
                region="US",
                language=None,
                is_original_title=False,
                attributes="complete title",
                types=None,
            ),
            aka_titles_table.Row(
                movie_imdb_id="tt0051554",
                sequence=1,
                title="Dracula",
                region="US",
                language=None,
                is_original_title=True,
                attributes="original title",
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
            ),
            release_dates_table.Row(
                movie_imdb_id="tt0051554",
                release_date=datetime.date(1958, 5, 8),
                notes="",
            ),
            release_dates_table.Row(
                movie_imdb_id="tt0098327",
                release_date=datetime.date(1989, 5, 19),
                notes="",
            ),
        ]
    )

    countries_table.reload(
        [
            countries_table.Row(movie_imdb_id="tt0053221", country="United States"),
            countries_table.Row(movie_imdb_id="tt0051554", country="United Kingdom"),
            countries_table.Row(movie_imdb_id="tt0098327", country="Austria"),
        ]
    )

    genres_table.reload([genres_table.Row(movie_imdb_id="tt0053221", genre="Western")])

    sort_titles_table.reload(
        [
            sort_titles_table.Row(movie_imdb_id="tt0053221", sort_title="Rio Bravo"),
            sort_titles_table.Row(
                movie_imdb_id="tt0051554", sort_title="Horror of Dracula"
            ),
            sort_titles_table.Row(
                movie_imdb_id="tt0098327", sort_title="Seventh Continent"
            ),
        ]
    )

    directing_credits_table.reload(
        [
            directing_credits_table.Row(
                movie_imdb_id="tt0053221",
                person_imdb_id="nm0001328",
                sequence=0,
                notes="",
            ),
            directing_credits_table.Row(
                movie_imdb_id="tt0051554",
                person_imdb_id="nm0279807",
                sequence=0,
                notes="",
            ),
            directing_credits_table.Row(
                movie_imdb_id="tt0098327",
                person_imdb_id="nm0359734",
                sequence=0,
                notes="",
            ),
        ]
    )

    reviews_table.reload(
        [
            reviews_table.Row(
                movie_imdb_id="tt0053221",
                date=datetime.date(2021, 1, 29),
                grade="A+",
                grade_value=6,
                slug="rio-bravo-1959",
            ),
            reviews_table.Row(
                movie_imdb_id="tt0051554",
                date=datetime.date(2021, 3, 12),
                grade="A",
                grade_value=5,
                slug="horror-of-dracula-1958",
            ),
            reviews_table.Row(
                movie_imdb_id="tt0098327",
                date=datetime.date(2021, 10, 31),
                grade="A",
                grade_value=5,
                slug="the-seventh-continent-1989",
            ),
        ]
    )


def test_exports_reviewed_movies(tmp_path: str) -> None:
    expected = [
        {
            "imdbId": "tt0051554",
            "title": "Horror of Dracula",
            "year": 1958,
            "releaseDate": "1958-05-08",
            "slug": "horror-of-dracula-1958",
            "sortTitle": "Horror of Dracula",
            "runtimeMinutes": 98,
            "directorNames": ["Terence Fisher"],
            "principalCastNames": ["Peter Cushing", "Christopher Lee"],
            "countries": ["United Kingdom"],
            "originalTitle": "Dracula",
            "grade": "A",
            "gradeValue": 5,
            "reviewDate": "2021-03-12",
            "reviewYear": "2021",
            "genres": [],
        },
        {
            "imdbId": "tt0053221",
            "title": "Rio Bravo",
            "year": 1959,
            "releaseDate": "1959-03-18",
            "slug": "rio-bravo-1959",
            "sortTitle": "Rio Bravo",
            "runtimeMinutes": 141,
            "directorNames": ["Howard Hawks"],
            "principalCastNames": ["John Wayne", "Dean Martin", "Ricky Nelson"],
            "countries": ["United States"],
            "originalTitle": None,
            "grade": "A+",
            "gradeValue": 6,
            "reviewDate": "2021-01-29",
            "reviewYear": "2021",
            "genres": ["Western"],
        },
        {
            "imdbId": "tt0098327",
            "title": "The Seventh Continent",
            "year": 1989,
            "releaseDate": "1989-05-19",
            "slug": "the-seventh-continent-1989",
            "sortTitle": "Seventh Continent",
            "runtimeMinutes": 120,
            "directorNames": ["Michael Haneke"],
            "principalCastNames": [],
            "countries": ["Austria"],
            "originalTitle": "Der siebente Kontinent",
            "grade": "A",
            "gradeValue": 5,
            "reviewDate": "2021-10-31",
            "reviewYear": "2021",
            "genres": [],
        },
    ]

    reviewed_movies.export()

    with open(os.path.join(tmp_path, "reviewed_movies.json"), "r") as output_file:
        file_content = json.load(output_file)

    assert file_content == expected
