import os
from typing import Any
from unittest.mock import MagicMock

import pytest

from movielog.repository.datasets import extractor


@pytest.fixture(autouse=True)
def test_file(gzip_file: MagicMock) -> Any:
    return gzip_file(os.path.join(os.path.dirname(__file__), "extractor_test_data.tsv"))


def test_extractor_skips_incomplete_rows(test_file: str) -> None:
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

    assert list(extractor.extract(test_file)) == expected
