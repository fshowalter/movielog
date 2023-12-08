import shlex
import subprocess  # noqa: S404
from datetime import datetime
from os import makedirs, path
from urllib import request

from movielog.utils.logging import logger

DOWNLOAD_DIR = "downloads"
IMDB_BASE = "https://datasets.imdbws.com/"


def download(imdb_file_name: str) -> str:
    url = IMDB_BASE + imdb_file_name

    last_modified_date = get_last_modified_date(url)

    download_path = ensure_download_path(last_modified_date)

    local_file_path = path.join(download_path, imdb_file_name)

    if path.exists(local_file_path):
        logger.log("File {} already exists.", local_file_path)
    else:
        logger.log("Downloading {} to {}...", url, local_file_path)
        curl(url, local_file_path)

    return local_file_path


def curl(url: str, dest: str) -> None:
    cmd = "curl --fail --progress-bar -o {1} {0}".format(url, dest)
    args = shlex.split(cmd)
    subprocess.check_output(args, shell=False)  # noqa: S603


def get_last_modified_date(url: str) -> datetime:
    with request.urlopen(url) as response:  # noqa: S310
        last_modified_header = response.info().get("Last-Modified")
        last_modified_date = datetime.strptime(
            last_modified_header,
            "%a, %d %b %Y %H:%M:%S %Z",  # noqa: WPS323
        )
    logger.log(
        "Remote file {} last updated {}.", url.split("/")[-1], last_modified_date
    )
    return last_modified_date


def ensure_download_path(last_modified_date: datetime) -> str:
    download_path = path.join(
        DOWNLOAD_DIR,
        last_modified_date.strftime("%Y-%m-%d"),  # noqa: WPS323
    )

    if path.exists(download_path):
        logger.log("Directory {} already exists.", download_path)
    else:
        logger.log("Creating directory {}...", download_path)
        makedirs(download_path)

    return download_path
