from __future__ import annotations

import datetime
import json
import os

import pytest

from movielog.moviedata.core import movies_table, people_table
from movielog.moviedata.extended.tables import writing_credits_table
from movielog.viewings import viewings_table
from movielog.viewings.exports import most_watched_writers


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
                medium=None,
                medium_notes=None,
            ),
            viewings_table.Row(
                movie_imdb_id="tt0038355",
                date=datetime.date(2017, 3, 12),
                sequence=2,
                medium="Blu-ray",
                medium_notes=None,
                venue=None,
            ),
            viewings_table.Row(
                movie_imdb_id="tt6019206",
                date=datetime.date(2017, 4, 29),
                sequence=3,
                venue="New Beverly",
                medium=None,
                medium_notes=None,
            ),
            viewings_table.Row(
                movie_imdb_id="tt0089175",
                date=datetime.date(2017, 10, 30),
                sequence=4,
                venue="AFI Silver",
                medium=None,
                medium_notes=None,
            ),
            viewings_table.Row(
                movie_imdb_id="tt0089175",
                date=datetime.date(2017, 10, 31),
                sequence=5,
                venue="AFI Silver",
                medium=None,
                medium_notes=None,
            ),
        ]
    )


def test_exports_most_watched_writers(tmp_path: str) -> None:

    most_watched_writers.export()

    expected: dict[str, object] = {
        "viewingYear": "2016",
        "mostWatched": [],
    }

    with open(
        os.path.join(tmp_path, "most_watched_writers", "2016.json"), "r"
    ) as file2016:
        file_content = json.load(file2016)

    assert file_content == expected

    expected = {
        "viewingYear": "2017",
        "mostWatched": [
            {
                "imdbId": "nm0276169",
                "fullName": "Tom Holland",
                "viewingCount": 2,
                "viewing_sequence_ids": [4, 5],
            },
        ],
    }

    with open(
        os.path.join(tmp_path, "most_watched_writers", "2017.json"), "r"
    ) as file2017:
        file_content = json.load(file2017)

    assert file_content == expected

    expected = {
        "viewingYear": "all",
        "mostWatched": [
            {
                "imdbId": "nm0102824",
                "fullName": "Leigh Brackett",
                "viewingCount": 2,
                "viewing_sequence_ids": [1, 2],
            },
            {
                "imdbId": "nm0276169",
                "fullName": "Tom Holland",
                "viewingCount": 2,
                "viewing_sequence_ids": [4, 5],
            },
        ],
    }

    with open(
        os.path.join(tmp_path, "most_watched_writers", "all.json"), "r"
    ) as file_all:
        file_content = json.load(file_all)

    assert file_content == expected