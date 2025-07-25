from __future__ import annotations

from collections.abc import Callable, Generator, Sequence
from pathlib import Path
from shutil import copyfile

import pytest
from prompt_toolkit.application.current import create_app_session
from prompt_toolkit.input import create_pipe_input
from pytest_mock import MockerFixture

MockInput = Callable[[Sequence[str]], None]


@pytest.fixture(autouse=True)
def mock_input() -> Generator[MockInput]:
    with create_pipe_input() as pipe_input, create_app_session(input=pipe_input):

        def factory(input_sequence: Sequence[str]) -> None:
            pipe_input.send_text("".join(input_sequence))

        yield factory


@pytest.fixture(autouse=True)
def copy_viewings_testdata(mocker: MockerFixture, tmp_path: Path) -> None:
    dirname = Path(__file__).parent
    Path(tmp_path / "viewings").mkdir(parents=True)

    for file_path in Path(dirname / "__testdata__", "viewings").glob("*.md"):
        target_path = tmp_path / "viewings" / Path(file_path).name
        copyfile(file_path, target_path)

    mocker.patch(
        "movielog.repository.markdown_viewings.FOLDER_NAME",
        tmp_path / "viewings",
    )


@pytest.fixture(autouse=True)
def copy_titles_testdata(mocker: MockerFixture, tmp_path: Path) -> None:
    dirname = Path(__file__).parent
    Path(tmp_path / "titles").mkdir(parents=True)

    for file_path in Path(dirname / "__testdata__", "titles").glob("*.json"):
        target_path = tmp_path / "titles" / Path(file_path).name
        copyfile(file_path, target_path)

    mocker.patch(
        "movielog.repository.json_titles.FOLDER_NAME",
        tmp_path / "titles",
    )
