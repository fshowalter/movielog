from typing import Any, Callable, Dict

import pytest

from movielog import yaml_file


class ConcreteMovie(yaml_file.Movie):  # noqa: WPS604
    @classmethod
    def from_yaml_object(
        cls, file_path: str, yaml_object: Dict[str, Any]
    ) -> "ConcreteMovie":
        """Test stub."""

    def generate_slug(self) -> str:
        """Test stub."""

    @classmethod
    def folder_path(cls) -> str:
        """Test stub."""

    def as_yaml(self) -> Dict[str, Any]:
        """Test stub."""


@pytest.fixture
def make_concrete_movie() -> Callable[..., yaml_file.Movie]:
    def _make_concrete_movie(
        title: str = "Rio Bravo", year: int = 1959
    ) -> yaml_file.Movie:
        return ConcreteMovie(
            file_path=None, imdb_id="tt0053221", title=title, year=year
        )

    return _make_concrete_movie
