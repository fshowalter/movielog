from typing import Any, List

import imdb
import pytest
from pytest_mock import MockFixture

from movielog import imdb_http


@pytest.fixture
def title_basic() -> imdb_http.TitleBasic:
    return imdb_http.TitleBasic(
        imdb_id="tt0092106", title="The Transformers: The Movie", year=1986,
    )


@pytest.fixture(autouse=True)
def imdb_scraper_mock(mocker: MockFixture) -> Any:
    mocker.patch.object(
        imdb_http.imdb_scraper, "get_movie", return_value=imdb.Movie.Movie()
    )
    return mocker.patch.object(imdb_http.imdb_scraper, "update",)


@pytest.fixture(autouse=True)
def reset_cache() -> Any:
    imdb_http.silent_ids = set()
    imdb_http.no_sound_mix_ids = set()


def test_returns_none_if_no_sound_mix(
    imdb_scraper_mock: MockFixture, title_basic: MockFixture
) -> None:
    def update_side_effect_no_technical(
        imdb_movie: imdb.Movie.Movie, info: List[str]  # noqa: WPS110
    ) -> None:
        imdb_movie["tech"] = {}

    imdb_scraper_mock.side_effect = update_side_effect_no_technical

    assert imdb_http.is_silent_film(title_basic) is None
    assert "tt0092106" in imdb_http.no_sound_mix_ids
    assert "tt0092106" not in imdb_http.silent_ids


def test_returns_true_if_sound_mix_and_silent(
    imdb_scraper_mock: MockFixture, title_basic: MockFixture
) -> None:
    def update_side_effect_technical_with_silent(
        imdb_movie: imdb.Movie.Movie, info: List[str]  # noqa: WPS110
    ) -> None:
        imdb_movie["tech"] = {"sound mix": ["Silent"]}

    imdb_scraper_mock.side_effect = update_side_effect_technical_with_silent

    assert imdb_http.is_silent_film(title_basic) is True
    assert "tt0092106" not in imdb_http.no_sound_mix_ids
    assert "tt0092106" in imdb_http.silent_ids


def test_returns_false_if_sound_mix_and_not_silent(
    imdb_scraper_mock: MockFixture, title_basic: MockFixture
) -> None:
    def update_side_effect_technical_without_silent(
        imdb_movie: imdb.Movie.Movie, info: List[str]  # noqa: WPS110
    ) -> None:
        imdb_movie["tech"] = {"sound mix": ["Dolby"]}

    imdb_scraper_mock.side_effect = update_side_effect_technical_without_silent

    assert imdb_http.is_silent_film(title_basic) is False
    assert "tt0092106" not in imdb_http.no_sound_mix_ids
    assert "tt0092106" not in imdb_http.silent_ids


def test_returns_true_if_in_silent_ids_cache(
    imdb_scraper_mock: MockFixture, title_basic: MockFixture
) -> None:
    imdb_http.silent_ids = set(["tt0092106"])

    assert imdb_http.is_silent_film(title_basic) is True


def test_returns_none_if_not_in_silent_ids_in_no_sound_mix_ids_cache(
    imdb_scraper_mock: MockFixture, title_basic: MockFixture
) -> None:
    imdb_http.no_sound_mix_ids = set(["tt0092106"])

    assert imdb_http.is_silent_film(title_basic) is None
