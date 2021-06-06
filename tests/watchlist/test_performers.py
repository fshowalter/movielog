import json
import os
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.watchlist import api as watchlist_api
from movielog.watchlist.movies import Movie


@pytest.fixture(autouse=True)
def mock_movies_for_performer(mocker: MockerFixture) -> None:
    movies = [
        Movie(
            title="Rio Bravo",
            year=1959,
            imdb_id="tt0053221",
            notes=None,
        )
    ]
    mocker.patch(
        "movielog.watchlist.performers.movies_for_performer",
        MagicMock(return_value=movies),
    )


def test_add_performer_serializes_performer(
    tmp_path: str,
) -> None:
    expected = {
        "frozen": False,
        "name": "John Wayne",
        "imdb_id": "nm0000078",
        "slug": "john-wayne",
        "movies": [
            {
                "title": "Rio Bravo",
                "year": 1959,
                "imdb_id": "tt0053221",
                "notes": None,
            }
        ],
    }

    watchlist_api.add_performer(imdb_id="nm0000078", name="John Wayne")

    with open(
        os.path.join(tmp_path, "performers", "john-wayne.json"), "r"
    ) as output_file:
        file_content = json.load(output_file)

    assert file_content == expected
