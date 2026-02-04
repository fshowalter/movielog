import shlex
import subprocess
from datetime import datetime
from pathlib import Path
from urllib import request

from movielog.utils.logging import logger

DOWNLOAD_DIR = "downloads"
IMDB_BASE = "https://datasets.imdbws.com/"


def download(imdb_file_name: str) -> Path:
    url = IMDB_BASE + imdb_file_name

    last_modified_date = get_last_modified_date(url)

    download_path = ensure_download_path(last_modified_date)

    local_file_path = Path(download_path) / imdb_file_name

    if local_file_path.exists():
        logger.log("File {} already exists.", local_file_path)
    else:
        logger.log("Downloading {} to {}...", url, local_file_path)
        curl(url, str(local_file_path))

    return local_file_path


def curl(url: str, dest: str) -> None:
    cmd = f"curl --fail --progress-bar -o {dest} {url}"
    args = shlex.split(cmd)
    subprocess.check_output(args, shell=False)  # noqa: S603


def get_last_modified_date(url: str) -> datetime:
    with request.urlopen(url) as response:  # noqa: S310
        last_modified_header = response.info().get("Last-Modified")
        last_modified_date = datetime.strptime(
            last_modified_header,
            "%a, %d %b %Y %H:%M:%S %Z",
        )
    logger.log(
        "Remote file {} last updated {}.", url.rsplit("/", maxsplit=1)[0], last_modified_date
    )
    return last_modified_date


def ensure_download_path(last_modified_date: datetime) -> Path:
    download_path = Path(DOWNLOAD_DIR) / last_modified_date.strftime("%Y-%m-%d")

    if download_path.exists():
        logger.log("Directory {} already exists.", download_path)
    else:
        logger.log("Creating directory {}...", download_path)
        download_path.mkdir(parents=True)

    return download_path
