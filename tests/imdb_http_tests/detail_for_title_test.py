from typing import Any

import pytest
from pytest_mock import MockFixture

from movielog import imdb_http


@pytest.fixture(autouse=True)
def imdb_scraper_mock(mocker: MockFixture) -> Any:
    return mocker.patch.object(
        imdb_http.imdb_scraper,
        "get_movie",
        return_value={
            "title": "The Transformers: The Movie",
            "year": 1986,
            "countries": ["United States", "Japan"],
        },
    )


def test_countries_for_title_from_imdb(imdb_scraper_mock: MockFixture,) -> None:
    expected_title_detail = imdb_http.TitleDetail(
        imdb_id="tt0092106",
        title="The Transformers: The Movie",
        year=1986,
        countries=["United States", "Japan"],
    )

    title_detail = imdb_http.countries_for_title(title_imdb_id="tt0092106")

    assert imdb_scraper_mock.called_once_with("0092106")
    assert title_detail == expected_title_detail
