import json
import os
from datetime import date

import pytest

from movielog.moviedata.core import movies_table
from movielog.viewings import viewings_table
from movielog.viewings.exports import viewing_stats


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
                principal_cast_ids="",
                votes=23,
                imdb_rating=7.8,
            ),
            movies_table.Row(
                imdb_id="tt0038355",
                title="The Big Sleep",
                original_title="The Big Sleep",
                year=1946,
                runtime_minutes=111,
                principal_cast_ids="",
                votes=123,
                imdb_rating=8.1,
            ),
            movies_table.Row(
                imdb_id="tt6019206",
                title="Kill Bill: The Whole Bloody Affair",
                original_title="Kill Bill: The Whole Bloody Affair",
                year=2011,
                runtime_minutes=247,
                principal_cast_ids="",
                votes=253,
                imdb_rating=6.1,
            ),
            movies_table.Row(
                imdb_id="tt0089175",
                title="Fright Night",
                original_title="Fright Night",
                year=1985,
                runtime_minutes=95,
                principal_cast_ids="",
                votes=263,
                imdb_rating=7.1,
            ),
        ]
    )

    viewings_table.reload(
        [
            viewings_table.Row(
                movie_imdb_id="tt0053221",
                date=date(2016, 3, 12),
                sequence=1,
                venue="AFI Silver",
                medium=None,
                medium_notes=None,
            ),
            viewings_table.Row(
                movie_imdb_id="tt0053221",
                date=date(2016, 6, 19),
                sequence=2,
                venue="Alamo Drafthouse",
                medium=None,
                medium_notes=None,
            ),
            viewings_table.Row(
                movie_imdb_id="tt0053221",
                date=date(2017, 1, 29),
                sequence=3,
                medium="Blu-ray",
                venue=None,
                medium_notes=None,
            ),
            viewings_table.Row(
                movie_imdb_id="tt0038355",
                date=date(2017, 4, 12),
                sequence=4,
                medium="Blu-ray",
                venue=None,
                medium_notes=None,
            ),
            viewings_table.Row(
                movie_imdb_id="tt6019206",
                date=date(2017, 4, 29),
                sequence=4,
                venue="New Beverly",
                medium=None,
                medium_notes=None,
            ),
            viewings_table.Row(
                movie_imdb_id="tt0089175",
                date=date(2017, 10, 31),
                sequence=4,
                venue="Alamo Drafthouse",
                medium=None,
                medium_notes=None,
            ),
        ]
    )


def test_exports_viewing_stats(tmp_path: str) -> None:
    viewing_stats.export()

    expected = {
        "viewingYear": "2016",
        "movieCount": 1,
        "newMovieCount": 1,
        "viewingCount": 2,
    }

    with open(os.path.join(tmp_path, "viewing_stats", "2016.json"), "r") as file2016:
        file_content = json.load(file2016)

    assert file_content == expected

    expected = {
        "viewingYear": "2017",
        "movieCount": 4,
        "newMovieCount": 3,
        "viewingCount": 4,
    }

    with open(os.path.join(tmp_path, "viewing_stats", "2017.json"), "r") as file2017:
        file_content = json.load(file2017)

    assert file_content == expected

    expected = {
        "viewingYear": "all",
        "movieCount": 4,
        "newMovieCount": 4,
        "viewingCount": 6,
    }

    with open(os.path.join(tmp_path, "viewing_stats", "all.json"), "r") as file_all:
        file_content = json.load(file_all)

    assert file_content == expected
