import os
from typing import Any
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.moviedata.core import extractor


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


def test_checkpoint_touches_success_file_when_complete(tmp_path: str) -> None:
    file_path = os.path.join(tmp_path, "extractor_test.tsv")
    expected = "{0}._success".format(file_path)

    for _ in extractor.checkpoint(file_path):  # noqa: WPS328
        pass  # noqa: WPS420

    assert os.path.exists(expected)


def test_checkpoint_does_not_yield_if_success_file_found(
    tmp_path: str, mocker: MockerFixture
) -> None:
    file_path = os.path.join(tmp_path, "extractor_test.tsv")
    open("{0}._success".format(file_path), "a").close()  # noqa: WPS515

    mock_action = mocker.Mock()

    for _ in extractor.checkpoint(file_path):  # pragma: no cover
        mock_action()

    mock_action.assert_not_called()
