import os
from typing import Any, Dict, Sequence

from pytest_mock import MockerFixture

import movielog.logger  # noqa: WPS301
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
        return {
            "imdb_id": self.imdb_id,
            "title": self.title,
        }


class ConcreteWithSequence(yaml_file.WithSequence):
    @classmethod
    def load_all(cls) -> Sequence["ConcreteWithSequence"]:
        """Test stub."""

    @classmethod
    def from_yaml_object(
        cls, file_path: str, yaml_object: Dict[str, Any]
    ) -> "ConcreteWithSequence":
        """Test stub."""

    def generate_slug(self) -> str:
        """Test stub."""

    @classmethod
    def folder_path(cls) -> str:
        """Test stub."""

    def as_yaml(self) -> Dict[str, Any]:
        return {
            "sequence": self.sequence,
        }


def test_logs_save(tmp_path: str, mocker: MockerFixture) -> None:
    file_path = os.path.join(tmp_path, "test_writes_yaml.yaml")
    mocker.patch("movielog.logger.logger.log")

    movie = ConcreteMovie(
        file_path=file_path, imdb_id="tt0053221", title="Rio Bravo", year=1959,
    )
    movie.save()

    movielog.logger.logger.log.assert_called_once_with("Wrote {}", file_path)  # type: ignore


def test_custom_log_function(tmp_path: str, mocker: MockerFixture) -> None:
    file_path = os.path.join(tmp_path, "test_writes_yaml.yaml")

    custom_log_function = mocker.stub(name="custom_log_function")

    movie = ConcreteMovie(
        file_path=file_path, imdb_id="tt0053221", title="Rio Bravo", year=1959,
    )
    movie.save(custom_log_function)

    custom_log_function.assert_called_once()


def test_handles_unicode(tmp_path: str) -> None:
    expected = "imdb_id: tt0309832\ntitle: Maléfique\n"

    file_path = os.path.join(tmp_path, "test_handles_unicode.yaml")

    movie = ConcreteMovie(
        file_path=file_path, imdb_id="tt0309832", title="Maléfique", year=1959,
    )
    movie.save()

    with open(str(file_path), "r") as output_file:
        yaml_content = output_file.read()

    assert yaml_content == expected


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


def test_creates_slug_if_no_filename(tmp_path: str, mocker: MockerFixture) -> None:
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


def test_preserves_sequence(tmp_path: str, mocker: MockerFixture) -> None:
    expected = "sequence: 33\n"

    mocker.patch.object(ConcreteWithSequence, "folder_path", lambda: tmp_path)

    movie = ConcreteWithSequence(file_path=None, sequence=33,)

    mocker.patch.object(movie, "generate_slug", lambda: "test_preserves_sequence")
    movie.save()

    file_path = os.path.join(tmp_path, "test_preserves_sequence.yml")

    with open(file_path, "r") as output_file:
        yaml_content = output_file.read()

    assert yaml_content == expected


def test_creates_directory_if_not_present(tmp_path: str, mocker: MockerFixture) -> None:
    expected = "imdb_id: tt0053221\ntitle: Rio Bravo\n"

    mocker.patch.object(ConcreteMovie, "folder_path", lambda: tmp_path)

    movie = ConcreteMovie(
        file_path=None, imdb_id="tt0053221", title="Rio Bravo", year=1959,
    )

    mocker.patch.object(
        movie, "generate_slug", lambda: "test_creates_slug_if_no_filename"
    )

    mocker.patch("os.path.exists").return_value = False
    mocker.patch("os.makedirs")

    movie.save()

    file_path = os.path.join(tmp_path, "test_creates_slug_if_no_filename.yml")

    with open(file_path, "r") as output_file:
        yaml_content = output_file.read()

    assert yaml_content == expected
    os.makedirs.assert_called_once_with(str(tmp_path))  # type: ignore
