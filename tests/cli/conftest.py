from __future__ import annotations

import os
from glob import glob
from pathlib import Path
from shutil import copyfile
from typing import Callable, Generator, Sequence

import pytest
from prompt_toolkit.application.current import create_app_session
from prompt_toolkit.input import create_pipe_input
from pytest_mock import MockerFixture

MockInput = Callable[[Sequence[str]], None]


@pytest.fixture(autouse=True, scope="function")
def mock_input() -> Generator[MockInput, None, None]:
    with create_pipe_input() as pipe_input:
        with create_app_session(input=pipe_input):

            def factory(input_sequence: Sequence[str]) -> None:  # noqa: WPS 430
                pipe_input.send_text("".join(input_sequence))

            yield factory


@pytest.fixture(autouse=True, scope="function")
def copy_viewings_testdata(mocker: MockerFixture, tmp_path: Path) -> None:
    dirname = os.path.dirname(__file__)
    os.makedirs(tmp_path / "viewings")

    for file_path in glob(os.path.join(dirname, "__testdata__", "viewings", "*.md")):
        target_path = tmp_path / "viewings" / Path(file_path).name
        copyfile(file_path, target_path)

    mocker.patch(
        "movielog.repository.markdown_viewings.FOLDER_NAME",
        tmp_path / "viewings",
    )


@pytest.fixture(autouse=True, scope="function")
def copy_titles_testdata(mocker: MockerFixture, tmp_path: Path) -> None:
    dirname = os.path.dirname(__file__)
    os.makedirs(tmp_path / "titles")

    for file_path in glob(os.path.join(dirname, "__testdata__", "titles", "*.json")):
        target_path = tmp_path / "titles" / Path(file_path).name
        copyfile(file_path, target_path)

    mocker.patch(
        "movielog.repository.json_titles.FOLDER_NAME",
        tmp_path / "titles",
    )
