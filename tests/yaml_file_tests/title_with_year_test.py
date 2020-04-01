from typing import Callable

import pytest

from movielog import yaml_file


@pytest.mark.parametrize(
    "title, year, expected", [("Rio Bravo", 1959, "Rio Bravo (1959)")]
)
def test_builds_string_with_title_and_year(
    make_concrete_movie: Callable[..., yaml_file.Movie],
    title: str,
    year: int,
    expected: str,
) -> None:
    movie = make_concrete_movie(title=title, year=year)

    test_result = movie.title_with_year

    assert test_result == expected
