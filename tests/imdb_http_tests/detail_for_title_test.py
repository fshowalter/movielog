from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog import imdb_http


@pytest.fixture(autouse=True)
def imdb_scraper_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(
        imdb_http.imdb_scraper,
        "get_movie",
        return_value={
            "title": "The Transformers: The Movie",
            "year": 1986,
            "countries": ["United States", "Japan"],
        },
    )


def test_countries_for_title_from_imdb(imdb_scraper_mock: MagicMock) -> None:
    expected_title_detail = imdb_http.TitleDetail(
        imdb_id="tt0092106",
        title="The Transformers: The Movie",
        year=1986,
        countries=["United States", "Japan"],
    )

    title_detail = imdb_http.countries_for_title(title_imdb_id="tt0092106")

    assert imdb_scraper_mock.called_once_with("0092106")
    assert title_detail == expected_title_detail
