import json
import os
from datetime import date

import pytest

from movielog.moviedata.core import movies_table
from movielog.viewings import viewings_table
from movielog.viewings.exports import top_media


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
                imdb_id="tt0051554",
                title="Horror of Dracula",
                original_title="Dracula",
                year=1958,
                runtime_minutes=111,
                principal_cast_ids="",
                votes=16,
                imdb_rating=7.1,
            ),
            movies_table.Row(
                imdb_id="tt0053220",
                title="Ride Lonesome",
                original_title="Ride Lonesome",
                year=1959,
                runtime_minutes=99,
                principal_cast_ids="",
                votes=8,
                imdb_rating=7.5,
            ),
            movies_table.Row(
                imdb_id="tt0087298",
                title="Friday the 13th: The Final Chapter (1984)",
                original_title="Friday the 13th: The Final Chapter (1984)",
                year=1984,
                runtime_minutes=92,
                principal_cast_ids="",
                votes=12,
                imdb_rating=4.3,
            ),
            movies_table.Row(
                imdb_id="tt0089175",
                title="Fright Night",
                original_title="Fright Night",
                year=1985,
                runtime_minutes=95,
                principal_cast_ids="",
                votes=19,
                imdb_rating=5.3,
            ),
        ]
    )

    viewings_table.reload(
        [
            viewings_table.Row(
                sequence=1,
                movie_imdb_id="tt0053220",
                medium="Vudu",
                date=date(2016, 3, 12),
                medium_notes=None,
                venue=None,
            ),
            viewings_table.Row(
                sequence=2,
                movie_imdb_id="tt0053221",
                medium="Blu-ray",
                date=date(2016, 4, 10),
                medium_notes=None,
                venue=None,
            ),
            viewings_table.Row(
                sequence=3,
                movie_imdb_id="tt0089175",
                medium="Blu-ray",
                date=date(2016, 10, 31),
                medium_notes=None,
                venue=None,
            ),
            viewings_table.Row(
                sequence=1,
                movie_imdb_id="tt0087298",
                medium="Vudu",
                date=date(2017, 3, 12),
                medium_notes=None,
                venue=None,
            ),
            viewings_table.Row(
                sequence=2,
                movie_imdb_id="tt0051554",
                medium="Blu-ray",
                date=date(2017, 4, 10),
                medium_notes=None,
                venue=None,
            ),
        ]
    )


def test_exports_viewing_counts_for_media(tmp_path: str) -> None:
    top_media.export()

    expected = {
        "viewingYear": "2016",
        "totalViewingCount": 3,
        "stats": [
            {
                "name": "Blu-ray",
                "viewingCount": 2,
            },
            {
                "name": "Vudu",
                "viewingCount": 1,
            },
        ],
    }

    with open(os.path.join(tmp_path, "top_media", "2016.json"), "r") as file2016:
        file_content = json.load(file2016)

    assert file_content == expected

    expected = {
        "viewingYear": "2017",
        "totalViewingCount": 2,
        "stats": [
            {
                "name": "Vudu",
                "viewingCount": 1,
            },
            {
                "name": "Blu-ray",
                "viewingCount": 1,
            },
        ],
    }

    with open(os.path.join(tmp_path, "top_media", "2017.json"), "r") as file2017:
        file_content = json.load(file2017)

    assert file_content == expected

    expected = {
        "viewingYear": "all",
        "totalViewingCount": 5,
        "stats": [
            {
                "name": "Blu-ray",
                "viewingCount": 3,
            },
            {
                "name": "Vudu",
                "viewingCount": 2,
            },
        ],
    }

    with open(os.path.join(tmp_path, "top_media", "all.json"), "r") as file_all:
        file_content = json.load(file_all)

    assert file_content == expected