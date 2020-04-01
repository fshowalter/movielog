from typing import Callable, Tuple

import pytest

from movielog import yaml_file


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("Rio Bravo (1959)", ("Rio Bravo", 1959)),
        ("Blade Runner 2049 (2017)", ("Blade Runner 2049", 2017)),
    ],
)
def test_splits_movie_and_year(
    make_concrete_movie: Callable[..., yaml_file.Movie],
    test_input: str,
    expected: Tuple[str, int],
) -> None:
    movie = make_concrete_movie()

    test_result = movie.split_title_and_year(test_input)

    assert test_result == expected


@pytest.mark.parametrize(
    "test_input", ["Rio Bravo 1959", "Blade Runner"],
)
def test_throws_exception_when_cannot_split(
    make_concrete_movie: Callable[..., yaml_file.Movie], test_input: str
) -> None:
    movie = make_concrete_movie()

    with pytest.raises(yaml_file.YamlError):
        movie.split_title_and_year(test_input)
