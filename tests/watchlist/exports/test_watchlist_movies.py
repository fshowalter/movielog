import datetime
import json
import os

import pytest

from movielog.moviedata.core import movies_table, people_table
from movielog.moviedata.extended.tables import (
    countries_table,
    release_dates_table,
    sort_titles_table,
)
from movielog.watchlist import watchlist_table
from movielog.watchlist.exports import watchlist_movies


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
                principal_cast_ids="nm0000078",
                votes=23,
            ),
            movies_table.Row(
                imdb_id="tt0190590",
                title="O Brother, Where Art Thou?",
                original_title="Original Rio Bravo",
                year=2000,
                runtime_minutes=121,
                principal_cast_ids="",
                votes=-16,
            ),
            movies_table.Row(
                imdb_id="tt0055928",
                title="Dr. No",
                original_title="Dr. No",
                year=1962,
                runtime_minutes=111,
                principal_cast_ids="",
                votes=40,
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
                imdb_id="nm0001054",
                full_name="Joel Cohen",
                known_for_title_ids="",
            ),
            people_table.Row(
                imdb_id="nm0001053",
                full_name="Ethan Cohen",
                known_for_title_ids="",
            ),
            people_table.Row(
                imdb_id="nm0102824",
                full_name="Leigh Brackett",
                known_for_title_ids="",
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
                movie_imdb_id="tt0190590",
                release_date=datetime.date(2000, 5, 13),
                notes="(Cannes Film Festival)",
            ),
            release_dates_table.Row(
                movie_imdb_id="tt0055928",
                release_date=datetime.date(1962, 10, 5),
                notes="(London) (premiere)",
            ),
        ]
    )

    countries_table.reload(
        [
            countries_table.Row(movie_imdb_id="tt0053221", country="United States"),
            countries_table.Row(movie_imdb_id="tt0190590", country="United Kingdom"),
            countries_table.Row(movie_imdb_id="tt0190590", country="United States"),
            countries_table.Row(movie_imdb_id="tt0190590", country="France"),
            countries_table.Row(movie_imdb_id="tt0055928", country="United Kingdom"),
        ]
    )

    sort_titles_table.reload(
        [
            sort_titles_table.Row(movie_imdb_id="tt0053221", sort_title="Rio Bravo"),
            sort_titles_table.Row(
                movie_imdb_id="tt0190590", sort_title="O Brother, Where Art Thou?"
            ),
            sort_titles_table.Row(movie_imdb_id="tt0055928", sort_title="Dr. No"),
        ]
    )

    watchlist_table.reload(
        [
            watchlist_table.Row(
                movie_imdb_id="tt0053221",
                director_imdb_id="nm0001328",
                slug="howard-hawks",
                performer_imdb_id=None,
                writer_imdb_id=None,
                collection_name=None,
            ),
            watchlist_table.Row(
                movie_imdb_id="tt0190590",
                director_imdb_id="nm0001054",
                slug="the-coen-brothers",
                performer_imdb_id=None,
                writer_imdb_id=None,
                collection_name=None,
            ),
            watchlist_table.Row(
                movie_imdb_id="tt0053221",
                director_imdb_id=None,
                slug="john-wayne",
                performer_imdb_id="nm0000078",
                writer_imdb_id=None,
                collection_name=None,
            ),
            watchlist_table.Row(
                movie_imdb_id="tt0053221",
                director_imdb_id=None,
                slug="dean-martin",
                performer_imdb_id="nm0001509",
                writer_imdb_id=None,
                collection_name=None,
            ),
            watchlist_table.Row(
                movie_imdb_id="tt0053221",
                director_imdb_id=None,
                slug="leigh-brackett",
                performer_imdb_id=None,
                writer_imdb_id="nm0102824",
                collection_name=None,
            ),
            watchlist_table.Row(
                movie_imdb_id="tt0055928",
                director_imdb_id=None,
                slug="james-bond",
                performer_imdb_id=None,
                writer_imdb_id=None,
                collection_name="James Bond",
            ),
        ]
    )


def test_exports_watchlist_movies(tmp_path: str) -> None:
    expected = [
        {
            "imdb_id": "tt0053221",
            "title": "Rio Bravo",
            "year": 1959,
            "sort_title": "Rio Bravo",
            "release_date": "1959-03-18",
            "director_imdb_ids": ["nm0001328"],
            "performer_imdb_ids": ["nm0000078", "nm0001509"],
            "writer_imdb_ids": ["nm0102824"],
            "collection_names": [],
        },
        {
            "imdb_id": "tt0055928",
            "title": "Dr. No",
            "year": 1962,
            "sort_title": "Dr. No",
            "release_date": "1962-10-05",
            "director_imdb_ids": [],
            "performer_imdb_ids": [],
            "writer_imdb_ids": [],
            "collection_names": ["James Bond"],
        },
        {
            "imdb_id": "tt0190590",
            "title": "O Brother, Where Art Thou?",
            "year": 2000,
            "sort_title": "O Brother, Where Art Thou?",
            "release_date": "2000-05-13",
            "director_imdb_ids": ["nm0001054"],
            "performer_imdb_ids": [],
            "writer_imdb_ids": [],
            "collection_names": [],
        },
    ]

    watchlist_movies.export()

    with open(os.path.join(tmp_path, "watchlist_movies.json"), "r") as output_file:
        file_content = json.load(output_file)

    assert file_content == expected
