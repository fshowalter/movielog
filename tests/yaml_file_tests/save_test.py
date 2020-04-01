import os
from typing import Any, Dict

from pytest_mock import MockFixture

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
        return {
            "imdb_id": self.imdb_id,
            "title": self.title,
        }


def test_logs_save() -> None:
    pass


def test_custom_log_function() -> None:
    pass


def test_handles_unicode() -> None:
    pass


def test_writes_yaml(tmp_path: str) -> None:
    expected = "imdb_id: tt0053221\ntitle: Rio Bravo\n"

    file_path = os.path.join(tmp_path, "test_writes_yaml.yaml")

    movie = ConcreteMovie(
        file_path=file_path, imdb_id="tt0053221", title="Rio Bravo", year=1959,
    )
    movie.save()

    with open(str(file_path), "r") as output_file:
        yaml_content = output_file.read()

    assert yaml_content == expected


def test_creates_slug_if_no_filename(tmp_path: str, mocker: MockFixture) -> None:
    expected = "imdb_id: tt0053221\ntitle: Rio Bravo\n"

    mocker.patch.object(ConcreteMovie, "folder_path", lambda: tmp_path)

    movie = ConcreteMovie(
        file_path=None, imdb_id="tt0053221", title="Rio Bravo", year=1959,
    )

    mocker.patch.object(
        movie, "generate_slug", lambda: "test_creates_slug_if_no_filename"
    )
    movie.save()

    file_path = os.path.join(tmp_path, "test_creates_slug_if_no_filename.yml")

    with open(file_path, "r") as output_file:
        yaml_content = output_file.read()

    assert yaml_content == expected
