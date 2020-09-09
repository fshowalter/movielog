import os

import pytest
from pytest_mock import MockerFixture

from movielog import imdb_s3_downloader

original_download_dir = imdb_s3_downloader.DOWNLOAD_DIR


@pytest.fixture(autouse=True)
def mock_imdb_s3_downloader_download_path(
    mocker: MockerFixture, tmp_path: str
) -> MockerFixture:
    return mocker.patch(
        "movielog.imdb_s3_downloader.DOWNLOAD_DIR",
        os.path.join(tmp_path, original_download_dir),
    )


@pytest.fixture(autouse=True)
def subprocess_mock(mocker: MockerFixture) -> MockerFixture:
    return mocker.patch("movielog.imdb_s3_downloader.subprocess.check_output")


@pytest.fixture(autouse=True)
def request_mock(mocker: MockerFixture) -> MockerFixture:
    url_open_mock = mocker.patch("movielog.imdb_s3_downloader.request.urlopen")

    url_open_mock.return_value.__enter__.return_value.info.return_value = {  # noqa: E501, WPS110, WPS219, WPS609
        "Last-Modified": "Sat, 04 Apr 2020 12:00:00 GMT"
    }

    return url_open_mock


def test_creates_download_folder_based_on_request_date(
    request_mock: MockerFixture, tmp_path: str,
) -> None:
    folder_path = os.path.join(tmp_path, original_download_dir, "2020-04-04")
    expected = os.path.join(folder_path, "test.tsv.gz")

    assert imdb_s3_downloader.download("test.tsv.gz") == expected


def test_does_not_fail_if_already_exists(tmp_path: str) -> None:
    folder_path = os.path.join(tmp_path, original_download_dir, "2020-04-04")
    os.makedirs(folder_path)
    expected = os.path.join(folder_path, "test.tsv.gz")

    assert imdb_s3_downloader.download("test.tsv.gz") == expected


def test_skips_download_if_file_already_exists(
    subprocess_mock: MockerFixture, tmp_path: str
) -> None:
    folder_path = os.path.join(tmp_path, original_download_dir, "2020-04-04")
    os.makedirs(folder_path)
    expected = os.path.join(folder_path, "test.tsv.gz")
    open(expected, "a").close()  # noqa: WPS515

    assert imdb_s3_downloader.download("test.tsv.gz") == expected
    subprocess_mock.assert_not_called()


def test_calls_curl_with_the_correct_args(
    subprocess_mock: MockerFixture, tmp_path: str
) -> None:
    folder_path = os.path.join(tmp_path, original_download_dir, "2020-04-04")
    expected_out = os.path.join(folder_path, "test.tsv.gz")

    expected_args = ["curl", "--fail", "--progress-bar", "-o", expected_out]
    assert imdb_s3_downloader.download("test.tsv.gz") == expected_out
    assert subprocess_mock.called_once_with(expected_args, shell=False)
