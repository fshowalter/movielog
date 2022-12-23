from __future__ import annotations

import datetime
import json
import os

import pytest

from movielog.moviedata.core import movies_table, people_table
from movielog.moviedata.extended.tables import performing_credits_table
from movielog.viewings import viewings_table
from movielog.viewings.exports import most_watched_performers


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
                medium=None,
                medium_notes=None,
            ),
            viewings_table.Row(
                movie_imdb_id="tt0038355",
                date=datetime.date(2017, 3, 12),
                sequence=2,
                medium="Blu-ray",
                venue=None,
                medium_notes=None,
            ),
            viewings_table.Row(
                movie_imdb_id="tt0031971",
                date=datetime.date(2017, 4, 29),
                sequence=3,
                venue="New Beverly",
                medium=None,
                medium_notes=None,
            ),
            viewings_table.Row(
                movie_imdb_id="tt0089175",
                date=datetime.date(2017, 10, 31),
                sequence=4,
                venue="AFI Silver",
                medium=None,
                medium_notes=None,
            ),
        ]
    )


def test_exports_most_watched_performers(tmp_path: str) -> None:

    most_watched_performers.export()

    expected: dict[str, object] = {
        "viewingYear": "2016",
        "mostWatched": [],
    }

    with open(
        os.path.join(tmp_path, "most_watched_performers", "2016.json"), "r"
    ) as file2016:
        file_content = json.load(file2016)

    assert file_content == expected

    expected = {
        "viewingYear": "2017",
        "mostWatched": [],
    }

    with open(
        os.path.join(tmp_path, "most_watched_performers", "2017.json"), "r"
    ) as file2017:
        file_content = json.load(file2017)

    assert file_content == expected

    expected = {
        "viewingYear": "all",
        "mostWatched": [
            {
                "imdbId": "nm0000078",
                "fullName": "John Wayne",
                "viewingCount": 2,
                "viewing_sequence_ids": [1, 3],
            },
        ],
    }

    with open(
        os.path.join(tmp_path, "most_watched_performers", "all.json"), "r"
    ) as file_all:
        file_content = json.load(file_all)

    assert file_content == expected
