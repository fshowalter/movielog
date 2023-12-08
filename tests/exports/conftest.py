from __future__ import annotations

import os
from glob import glob
from pathlib import Path
from shutil import copyfile

import pytest
from pytest_mock import MockerFixture


@pytest.fixture(autouse=True, scope="function")
def copy_viewings_testdata(mocker: MockerFixture, tmp_path: Path) -> None:
    dirname = os.path.dirname(__file__)
    os.makedirs(tmp_path / "viewings")

    for file_path in glob(os.path.join(dirname, "__testdata__", "viewings", "*.json")):
        target_path = tmp_path / "viewings" / Path(file_path).name
        copyfile(file_path, target_path)

    mocker.patch(
        "movielog.repository.json_viewings.FOLDER_NAME",
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
