import datetime
import json
import os

import pytest

from movielog.moviedata.core import movies_table, people_table
from movielog.moviedata.extended.tables import directing_credits_table
from movielog.reviews import reviews_table, viewings_table
from movielog.reviews.exports import most_watched_directors
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
            ),
            movies_table.Row(
                imdb_id="tt0038355",
                title="The Big Sleep",
                original_title="The Big Sleep",
                year=1946,
                runtime_minutes=111,
                principal_cast_ids="",
            ),
            movies_table.Row(
                imdb_id="tt6019206",
                title="Kill Bill: The Whole Bloody Affair",
                original_title="Kill Bill: The Whole Bloody Affair",
                year=2011,
                runtime_minutes=247,
                principal_cast_ids="",
            ),
            movies_table.Row(
                imdb_id="tt0089175",
                title="Fright Night",
                original_title="Fright Night",
                year=1985,
                runtime_minutes=95,
                principal_cast_ids="",
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

    directing_credits_table.reload(
        [
            directing_credits_table.Row(
                movie_imdb_id="tt0053221",
                person_imdb_id="nm0001328",
                sequence=0,
                notes="",
            ),
            directing_credits_table.Row(
                movie_imdb_id="tt0038355",
                person_imdb_id="nm0001328",
                sequence=0,
                notes="",
            ),
            directing_credits_table.Row(
                movie_imdb_id="tt6019206",
                person_imdb_id="nm0000233",
                sequence=0,
                notes="",
            ),
            directing_credits_table.Row(
                movie_imdb_id="tt0089175",
                person_imdb_id="nm0276169",
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
                movie_imdb_id="tt6019206",
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
                director_imdb_id="nm0001328",
                slug="howard-hawks",
                performer_imdb_id=None,
                writer_imdb_id=None,
                collection_name=None,
            ),
            watchlist_table.Row(
                movie_imdb_id="tt0038355",
                director_imdb_id="nm0001328",
                slug="howard-hawks",
                performer_imdb_id=None,
                writer_imdb_id=None,
                collection_name=None,
            ),
            watchlist_table.Row(
                movie_imdb_id="tt6019206",
                director_imdb_id="nm0000233",
                slug="quentin-tarantino",
                performer_imdb_id=None,
                writer_imdb_id=None,
                collection_name=None,
            ),
        ]
    )


def test_exports_most_watched_directors(tmp_path: str) -> None:

    most_watched_directors.export()

    expected = {
        "viewing_year": "2016",
        "most_watched": [
            {
                "imdb_id": "nm0001328",
                "full_name": "Howard Hawks",
                "slug": "howard-hawks",
                "viewing_count": 1,
                "viewings": [
                    {
                        "venue": "Alamo Drafthouse",
                        "date": "2016-06-19",
                        "movie": {
                            "title": "Rio Bravo",
                            "year": 1959,
                            "slug": "rio-bravo-1959",
                        },
                    }
                ],
            },
        ],
    }

    with open(
        os.path.join(tmp_path, "most_watched_directors", "2016.json"), "r"
    ) as file2016:
        file_content = json.load(file2016)

    assert file_content == expected

    expected = {
        "viewing_year": "2017",
        "most_watched": [
            {
                "imdb_id": "nm0001328",
                "full_name": "Howard Hawks",
                "slug": "howard-hawks",
                "viewing_count": 1,
                "viewings": [
                    {
                        "venue": "Blu-ray",
                        "date": "2017-03-12",
                        "movie": {
                            "title": "The Big Sleep",
                            "year": 1946,
                            "slug": "the-big-sleep-1946",
                        },
                    }
                ],
            },
            {
                "imdb_id": "nm0000233",
                "full_name": "Quentin Tarantino",
                "slug": "quentin-tarantino",
                "viewing_count": 1,
                "viewings": [
                    {
                        "venue": "New Beverly",
                        "date": "2017-04-29",
                        "movie": {
                            "title": "Kill Bill: The Whole Bloody Affair",
                            "year": 2011,
                            "slug": "kill-bill-the-whole-bloody-affair-2011",
                        },
                    }
                ],
            },
            {
                "imdb_id": "nm0276169",
                "full_name": "Tom Holland",
                "slug": None,
                "viewing_count": 1,
                "viewings": [
                    {
                        "venue": "AFI Silver",
                        "date": "2017-10-31",
                        "movie": {
                            "title": "Fright Night",
                            "year": 1985,
                            "slug": "fright-night-1985",
                        },
                    }
                ],
            },
        ],
    }

    with open(
        os.path.join(tmp_path, "most_watched_directors", "2017.json"), "r"
    ) as file2017:
        file_content = json.load(file2017)

    assert file_content == expected

    expected = {
        "viewing_year": "all",
        "most_watched": [
            {
                "imdb_id": "nm0001328",
                "full_name": "Howard Hawks",
                "slug": "howard-hawks",
                "viewing_count": 2,
                "viewings": [
                    {
                        "venue": "Alamo Drafthouse",
                        "date": "2016-06-19",
                        "movie": {
                            "title": "Rio Bravo",
                            "year": 1959,
                            "slug": "rio-bravo-1959",
                        },
                    },
                    {
                        "venue": "Blu-ray",
                        "date": "2017-03-12",
                        "movie": {
                            "title": "The Big Sleep",
                            "year": 1946,
                            "slug": "the-big-sleep-1946",
                        },
                    },
                ],
            },
            {
                "imdb_id": "nm0000233",
                "full_name": "Quentin Tarantino",
                "slug": "quentin-tarantino",
                "viewing_count": 1,
                "viewings": [
                    {
                        "venue": "New Beverly",
                        "date": "2017-04-29",
                        "movie": {
                            "title": "Kill Bill: The Whole Bloody Affair",
                            "year": 2011,
                            "slug": "kill-bill-the-whole-bloody-affair-2011",
                        },
                    }
                ],
            },
            {
                "imdb_id": "nm0276169",
                "full_name": "Tom Holland",
                "slug": None,
                "viewing_count": 1,
                "viewings": [
                    {
                        "venue": "AFI Silver",
                        "date": "2017-10-31",
                        "movie": {
                            "title": "Fright Night",
                            "year": 1985,
                            "slug": "fright-night-1985",
                        },
                    }
                ],
            },
        ],
    }

    with open(
        os.path.join(tmp_path, "most_watched_directors", "all.json"), "r"
    ) as file_all:
        file_content = json.load(file_all)

    assert file_content == expected
