import datetime
import json
import os

import pytest

from movielog.moviedata.core import movies_table
from movielog.moviedata.extended.tables import (
    genres_table,
    release_dates_table,
    sort_titles_table,
)
from movielog.viewings import viewings_table
from movielog.viewings.exports import viewings
from movielog.viewings.viewing import Viewing


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
                votes=8,
                imdb_rating=6.1,
            )
        ]
    )

    genres_table.reload([genres_table.Row(movie_imdb_id="tt0053221", genre="Western")])

    release_dates_table.reload(
        [
            release_dates_table.Row(
                movie_imdb_id="tt0053221",
                release_date=datetime.date(1959, 3, 18),
                notes="",
            )
        ]
    )

    sort_titles_table.reload(
        [sort_titles_table.Row(movie_imdb_id="tt0053221", sort_title="Rio Bravo")]
    )

    viewings_table.update(
        [
            Viewing(
                sequence=1,
                date=datetime.date(2021, 1, 29),
                imdb_id="tt0053221",
                slug="rio-bravo-1959",
                medium="Blu-ray",
                venue=None,
                medium_notes=None,
            )
        ]
    )


def test_exports_viewings(tmp_path: str) -> None:
    expected = [
        {
            "imdbId": "tt0053221",
            "title": "Rio Bravo",
            "year": 1959,
            "viewingDate": "2021-01-29",
            "sequence": 1,
            "genres": ["Western"],
            "viewingYear": "2021",
            "releaseDate": "1959-03-18",
            "sortTitle": "Rio Bravo",
            "medium": "Blu-ray",
            "venue": None,
            "mediumNotes": None,
        }
    ]

    viewings.export()

    with open(os.path.join(tmp_path, "viewings.json"), "r") as output_file:
        file_content = json.load(output_file)

    assert file_content == expected
