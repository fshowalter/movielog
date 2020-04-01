from typing import Any, Callable, Dict

import pytest

from movielog import yaml_file


class ConcreteMovie(yaml_file.Movie):  # noqa: WPS604
    @classmethod
    def from_yaml_object(cls, yaml_object: Dict[str, Any]) -> "ConcreteMovie":
        raise NotImplementedError

    def generate_slug(self) -> str:
        raise NotImplementedError

    @classmethod
    def folder_path(cls) -> str:
        raise NotImplementedError

    def as_yaml(self) -> Dict[str, Any]:
        raise NotImplementedError


@pytest.fixture
def make_concrete_movie() -> Callable[..., yaml_file.Movie]:
    def _make_concrete_movie(
        title: str = "Rio Bravo", year: int = 1959
    ) -> yaml_file.Movie:
        return ConcreteMovie(
            file_path=None, imdb_id="tt0053221", title=title, year=year
        )

    return _make_concrete_movie
