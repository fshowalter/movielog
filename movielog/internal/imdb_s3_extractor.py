import gzip
import pathlib
from typing import Generator, List, Optional

from movielog.logger import logger

ListOfOptionalStrings = List[Optional[str]]


def extract(
    file_path: str,
) -> Generator[ListOfOptionalStrings, None, None]:  # noqa: TAE002
    logger.log("Begin extracting from {0}...", file_path)

    with gzip.open(filename=file_path, mode="rt", encoding="utf-8") as gz_file:
        headers_length = len(gz_file.readline().strip().split("\t"))
        for line in gz_file:
            fields = line.strip().split("\t")
            if len(fields) != headers_length:
                continue

            yield _parse_fields(fields)


def checkpoint(file_path: str) -> Generator[None, None, None]:
    success_file = pathlib.Path("{0}._success".format(file_path))

    if success_file.exists():
        logger.log("Found {0} file. Skipping load.", success_file)
        return

    yield

    success_file.touch()


def _parse_fields(fields: List[Optional[str]]) -> List[Optional[str]]:  # noqa: WPS221
    for index, field in enumerate(fields):
        if field == r"\N":
            fields[index] = None

    return fields
