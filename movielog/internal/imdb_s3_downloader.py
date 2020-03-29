import shlex
import subprocess  # noqa: S404
from datetime import datetime
from os import makedirs, path
from urllib import request

from movielog.logger import logger

IMDB_BASE = "https://datasets.imdbws.com/"


def download(imdb_file_name: str, local_download_dir: str) -> str:
    url = IMDB_BASE + imdb_file_name

    last_modified_date = _get_last_modified_date(url)

    download_path = _ensure_download_path(local_download_dir, last_modified_date)

    local_file_path = path.join(download_path, imdb_file_name)

    if path.exists(local_file_path):
        logger.log("File {0} already exists.", local_file_path)
    else:
        logger.log("Downloading {0} to {1}...", url, local_file_path)
        _curl(url, local_file_path)

    return local_file_path


def _curl(url: str, dest: str) -> None:
    cmd = "curl --fail --progress-bar -o {1} {0}".format(url, dest)
    args = shlex.split(cmd)
    subprocess.check_output(args, shell=False)  # noqa: S603


def _get_last_modified_date(url: str) -> datetime:
    with request.urlopen(url) as response:  # noqa: S310
        last_modified_header = response.info().get("Last-Modified")
        last_modified_date = datetime.strptime(
            last_modified_header, "%a, %d %b %Y %H:%M:%S %Z",  # noqa: WPS323
        )
    logger.log(
        "Remote file {0} last updated {1}.", url.split("/")[-1], last_modified_date
    )
    return last_modified_date


def _ensure_download_path(download_root: str, last_modified_date: datetime) -> str:
    download_path = path.join(
        download_root, last_modified_date.strftime("%Y-%m-%d"),  # noqa: WPS323
    )

    if path.exists(download_path):
        logger.log("Directory {0} already exists.", download_path)
    else:
        logger.log("Creating directory {0}...", download_path)
        makedirs(download_path)

    return download_path
