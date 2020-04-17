import os
import shutil
from typing import Any

import pytest
from pytest_mock import MockFixture

from movielog import imdb_http, movies


@pytest.fixture(autouse=True)
def mock_folder_path(mocker: MockFixture, tmp_path: str) -> Any:
    folder_path = movies.FOLDER_PATH
    mocker.patch.object(movies, "FOLDER_PATH", os.path.join(tmp_path, folder_path))


@pytest.fixture(autouse=True)
def detail_for_title_mock(mocker: MockFixture) -> Any:
    return mocker.patch(
        "movielog.movies.imdb_http.countries_for_title",
        return_value=(
            imdb_http.TitleDetail(
                imdb_id="tt0092106",
                title="The Transformers: The Movie",
                year=1986,
                countries=["United States", "Japan"],
            )
        ),
    )


def test_creates_new_country_files_for_ones_that_do_not_exist(
    tmp_path: str, detail_for_title_mock: MockFixture,
) -> None:
    with open(
        os.path.join(os.path.dirname(__file__), "update_countries_test_output.yml"),
        "r",
    ) as expected_content_file:
        expected_file_content = expected_content_file.read()

    movies.update_countries(["tt0092106"])

    detail_for_title_mock.assert_called_once_with("tt0092106")

    with open(
        os.path.join(
            tmp_path, "movie_countries", "the-transformers-the-movie-1986.yml"
        ),
        "r",
    ) as new_file:
        assert new_file.read() == expected_file_content


def test_does_not_call_imdb_for_country_files_that_exist(
    tmp_path: str, detail_for_title_mock: MockFixture,
) -> None:
    output_path = os.path.join(tmp_path, "movie_countries")

    os.makedirs(output_path)

    with open(
        os.path.join(os.path.dirname(__file__), "update_countries_test_output.yml"),
        "r",
    ) as input_file:
        with open(
            os.path.join(output_path, "the-transformers-the-movie-1986.yml"), "w"
        ) as output_file:
            shutil.copyfileobj(input_file, output_file)

    movies.update_countries(["tt0092106"])

    detail_for_title_mock.assert_not_called()
