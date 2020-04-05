import os
from typing import Any

import pytest
from pytest_mock import MockFixture

from movielog import imdb_s3_extractor


@pytest.fixture(autouse=True)
def test_file(gzip_file: MockFixture) -> Any:
    return gzip_file(os.path.join(os.path.dirname(__file__), "extract_test_data.tsv"))


def test_skips_incomplete_rows(test_file: str) -> None:
    expected = [
        [
            "tt0053221",
            "movie",
            "Rio Bravo",
            "Rio Bravo",
            "0",
            "1959",
            None,
            "141",
            "Action,Drama,Western",
        ],
        [
            "tt0089175",
            "movie",
            "Fright Night",
            "Fright Night",
            "0",
            "1985",
            None,
            "106",
            "Horror,Thriller",
        ],
    ]

    assert list(imdb_s3_extractor.extract(test_file)) == expected
