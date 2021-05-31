import os
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.moviedata.core import downloader


@pytest.fixture(autouse=True)
def subprocess_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.moviedata.core.downloader.subprocess.check_output")


@pytest.fixture(autouse=True)
def request_mock(mocker: MockerFixture) -> MagicMock:
    url_open_mock = mocker.patch("movielog.moviedata.core.downloader.request.urlopen")

    magic_method_mock = url_open_mock.return_value.__enter__  # noqa: WPS609

    magic_method_mock.return_value.info.return_value = {
        "Last-Modified": "Sat, 04 Apr 2020 12:00:00 GMT"
    }

    return url_open_mock


def test_creates_download_folder_based_on_request_date() -> None:
    folder_path = os.path.join(downloader.DOWNLOAD_DIR, "2020-04-04")
    expected = os.path.join(folder_path, "test.tsv.gz")

    assert downloader.download("test.tsv.gz") == expected


def test_does_not_fail_if_already_exists() -> None:
    folder_path = os.path.join(downloader.DOWNLOAD_DIR, "2020-04-04")
    os.makedirs(folder_path)
    expected = os.path.join(folder_path, "test.tsv.gz")

    assert downloader.download("test.tsv.gz") == expected


def test_skips_download_if_file_already_exists(subprocess_mock: MagicMock) -> None:
    folder_path = os.path.join(downloader.DOWNLOAD_DIR, "2020-04-04")
    os.makedirs(folder_path)
    expected = os.path.join(folder_path, "test.tsv.gz")
    open(expected, "a").close()  # noqa: WPS515

    assert downloader.download("test.tsv.gz") == expected
    subprocess_mock.assert_not_called()


def test_calls_curl_with_the_correct_args(subprocess_mock: MagicMock) -> None:
    folder_path = os.path.join(downloader.DOWNLOAD_DIR, "2020-04-04")
    expected_out = os.path.join(folder_path, "test.tsv.gz")

    expected_args = ["curl", "--fail", "--progress-bar", "-o", expected_out]
    assert downloader.download("test.tsv.gz") == expected_out
    assert subprocess_mock.called_once_with(expected_args, shell=False)
