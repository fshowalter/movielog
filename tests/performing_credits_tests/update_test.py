import os
import shutil
from typing import Any
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog import imdb_http, performing_credits


@pytest.fixture(autouse=True)
def mock_folder_path(mocker: MockerFixture, tmp_path: str) -> Any:
    folder_path = performing_credits.FOLDER_PATH
    mocker.patch.object(
        performing_credits, "FOLDER_PATH", os.path.join(tmp_path, folder_path)
    )


@pytest.fixture(autouse=True)
def cast_credits_for_title_mock(mocker: MockerFixture) -> Any:
    return mocker.patch(
        "movielog.performing_credits.imdb_http.cast_credits_for_title",
        return_value=(
            imdb_http.TitleBasic(
                imdb_id="tt0092106",
                title="The Transformers: The Movie",
                year=1986,
            ),
            [
                imdb_http.CastCreditForTitle(
                    movie_imdb_id="tt0092106",
                    person_imdb_id="nm0191520",
                    name="Peter Cullen",
                    roles=["Optimus Prime", "Ironhide"],
                    notes="(voice)",
                    sequence=0,
                ),
                imdb_http.CastCreditForTitle(
                    movie_imdb_id="tt0092106",
                    person_imdb_id="nm0000080",
                    name="Orson Welles",
                    roles=["Unicrom"],
                    notes="(voice)",
                    sequence=1,
                ),
                imdb_http.CastCreditForTitle(
                    movie_imdb_id="tt0092106",
                    person_imdb_id="nm1084210",
                    name="Simon Furman",
                    roles=[],
                    notes="",
                    sequence=2,
                ),
            ],
        ),
    )


def test_creates_new_performing_credits_for_ones_that_do_not_exist(
    tmp_path: str,
    sql_query: MagicMock,
    cast_credits_for_title_mock: MagicMock,
) -> None:
    expected_rows = [
        ("tt0092106", "nm0191520", 0, "Optimus Prime / Ironhide", "(voice)"),
        ("tt0092106", "nm0000080", 1, "Unicrom", "(voice)"),
        ("tt0092106", "nm1084210", 2, "", ""),
    ]

    with open(
        os.path.join(os.path.dirname(__file__), "test_output.yml"), "r"
    ) as expected_content_file:
        expected_file_content = expected_content_file.read()

    performing_credits.update(["tt0092106"])

    cast_credits_for_title_mock.assert_called_once_with("tt0092106")

    with open(
        os.path.join(
            tmp_path, "performing_credits", "the-transformers-the-movie-1986.yml"
        ),
        "r",
    ) as new_file:
        assert new_file.read() == expected_file_content

    assert sql_query("SELECT * FROM 'performing_credits';") == expected_rows


def test_does_not_call_imdb_for_performing_credits_that_exist(
    tmp_path: str,
    sql_query: MagicMock,
    cast_credits_for_title_mock: MagicMock,
) -> None:
    expected_rows = [
        ("tt0092106", "nm0191520", 0, "Optimus Prime / Ironhide", "(voice)"),
        ("tt0092106", "nm0000080", 1, "Unicrom", "(voice)"),
        ("tt0092106", "nm1084210", 2, "", ""),
    ]

    output_path = os.path.join(tmp_path, "performing_credits")

    os.makedirs(output_path)

    with open(
        os.path.join(os.path.dirname(__file__), "test_output.yml"), "r"
    ) as input_file:
        with open(
            os.path.join(output_path, "the-transformers-the-movie-1986.yml"), "w"
        ) as output_file:
            shutil.copyfileobj(input_file, output_file)

    performing_credits.update(["tt0092106"])

    cast_credits_for_title_mock.assert_not_called()

    assert sql_query("SELECT * FROM 'performing_credits';") == expected_rows
