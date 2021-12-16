from __future__ import annotations

import datetime
import json
import os

import pytest

from movielog.moviedata.core import movies_table, people_table
from movielog.moviedata.extended.tables import writing_credits_table
from movielog.reviews import reviews_table, viewings_table
from movielog.reviews.exports import most_watched_writers
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
                imdb_rating=8.2,
            ),
            movies_table.Row(
                imdb_id="tt0038355",
                title="The Big Sleep",
                original_title="The Big Sleep",
                year=1946,
                runtime_minutes=111,
                principal_cast_ids="",
                votes=16,
                imdb_rating=7.9,
            ),
            movies_table.Row(
                imdb_id="tt6019206",
                title="Kill Bill: The Whole Bloody Affair",
                original_title="Kill Bill: The Whole Bloody Affair",
                year=2011,
                runtime_minutes=247,
                principal_cast_ids="",
                votes=8,
                imdb_rating=5.9,
            ),
            movies_table.Row(
                imdb_id="tt0089175",
                title="Fright Night",
                original_title="Fright Night",
                year=1985,
                runtime_minutes=95,
                principal_cast_ids="",
                votes=17,
                imdb_rating=6.4,
            ),
        ]
    )

    people_table.reload(
        [
            people_table.Row(
                imdb_id="nm0102824",
                full_name="Leigh Brackett",
                known_for_title_ids="",
            ),
            people_table.Row(
                imdb_id="nm0000233",
                full_name="Quentin Tarantino",
                known_for_title_ids="",
            ),
            people_table.Row(
                imdb_id="nm0276169",
                full_name="Tom Holland",
                known_for_title_ids="",
            ),
        ]
    )

    writing_credits_table.reload(
        [
            writing_credits_table.Row(
                movie_imdb_id="tt0053221",
                person_imdb_id="nm0102824",
                sequence=0,
                group_id=0,
                notes="",
            ),
            writing_credits_table.Row(
                movie_imdb_id="tt0038355",
                person_imdb_id="nm0102824",
                sequence=0,
                group_id=0,
                notes="",
            ),
            writing_credits_table.Row(
                movie_imdb_id="tt6019206",
                person_imdb_id="nm0000233",
                sequence=0,
                group_id=0,
                notes="",
            ),
            writing_credits_table.Row(
                movie_imdb_id="tt0089175",
                person_imdb_id="nm0276169",
                sequence=0,
                group_id=0,
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
                movie_imdb_id="tt6019206",
                date=datetime.date(2017, 4, 29),
                sequence=3,
                venue="New Beverly",
            ),
            viewings_table.Row(
                movie_imdb_id="tt0089175",
                date=datetime.date(2017, 10, 30),
                sequence=4,
                venue="AFI Silver",
            ),
            viewings_table.Row(
                movie_imdb_id="tt0089175",
                date=datetime.date(2017, 10, 31),
                sequence=5,
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
                movie_imdb_id="tt6019206",
                date=datetime.date(2017, 4, 29),
                sequence=3,
                grade="A",
                grade_value=5,
                slug="kill-bill-the-whole-bloody-affair-2011",
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
                slug="leigh-brackett",
                performer_imdb_id=None,
                writer_imdb_id="nm0102824",
                collection_name=None,
            ),
            watchlist_table.Row(
                movie_imdb_id="tt0038355",
                director_imdb_id=None,
                slug="leigh-brackett",
                performer_imdb_id=None,
                writer_imdb_id="nm0102824",
                collection_name=None,
            ),
            watchlist_table.Row(
                movie_imdb_id="tt6019206",
                director_imdb_id=None,
                slug="quentin-tarantino",
                performer_imdb_id=None,
                writer_imdb_id="nm0000233",
                collection_name=None,
            ),
        ]
    )


def test_exports_most_watched_writers(tmp_path: str) -> None:

    most_watched_writers.export()

    expected: dict[str, object] = {
        "viewing_year": "2016",
        "most_watched": [],
    }

    with open(
        os.path.join(tmp_path, "most_watched_writers", "2016.json"), "r"
    ) as file2016:
        file_content = json.load(file2016)

    assert file_content == expected

    expected = {
        "viewing_year": "2017",
        "most_watched": [
            {
                "imdb_id": "nm0276169",
                "full_name": "Tom Holland",
                "slug": None,
                "viewing_count": 2,
                "viewings": [
                    {
                        "sequence": 4,
                        "venue": "AFI Silver",
                        "date": "2017-10-30",
                        "title": "Fright Night",
                        "year": 1985,
                        "slug": "fright-night-1985",
                        "imdb_id": "tt0089175",
                    },
                    {
                        "sequence": 5,
                        "venue": "AFI Silver",
                        "date": "2017-10-31",
                        "title": "Fright Night",
                        "year": 1985,
                        "slug": "fright-night-1985",
                        "imdb_id": "tt0089175",
                    },
                ],
            },
        ],
    }

    with open(
        os.path.join(tmp_path, "most_watched_writers", "2017.json"), "r"
    ) as file2017:
        file_content = json.load(file2017)

    assert file_content == expected

    expected = {
        "viewing_year": "all",
        "most_watched": [
            {
                "imdb_id": "nm0102824",
                "full_name": "Leigh Brackett",
                "slug": "leigh-brackett",
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
                        "sequence": 2,
                        "venue": "Blu-ray",
                        "date": "2017-03-12",
                        "title": "The Big Sleep",
                        "year": 1946,
                        "slug": "the-big-sleep-1946",
                        "imdb_id": "tt0038355",
                    },
                ],
            },
            {
                "imdb_id": "nm0276169",
                "full_name": "Tom Holland",
                "slug": None,
                "viewing_count": 2,
                "viewings": [
                    {
                        "sequence": 4,
                        "venue": "AFI Silver",
                        "date": "2017-10-30",
                        "title": "Fright Night",
                        "year": 1985,
                        "slug": "fright-night-1985",
                        "imdb_id": "tt0089175",
                    },
                    {
                        "sequence": 5,
                        "venue": "AFI Silver",
                        "date": "2017-10-31",
                        "title": "Fright Night",
                        "year": 1985,
                        "slug": "fright-night-1985",
                        "imdb_id": "tt0089175",
                    },
                ],
            },
        ],
    }

    with open(
        os.path.join(tmp_path, "most_watched_writers", "all.json"), "r"
    ) as file_all:
        file_content = json.load(file_all)

    assert file_content == expected
