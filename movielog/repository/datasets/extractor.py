import gzip
from typing import Generator, Optional, Sequence

from movielog.utils.logging import logger

DatasetFields = list[Optional[str]]


def extract(
    file_path: str,
) -> Generator[DatasetFields, None, None]:  # noqa: TAE002
    logger.log("Begin extracting from {}...", file_path)

    with gzip.open(filename=file_path, mode="rt", encoding="utf-8") as gz_file:
        headers_length = len(gz_file.readline().strip().split("\t"))
        for line in gz_file:
            fields: Sequence[Optional[str]] = line.strip().split("\t")
            if len(fields) != headers_length:
                continue

            yield parse_fields(fields)


def parse_fields(
    fields: Sequence[Optional[str]],
) -> DatasetFields:
    parsed_fields: DatasetFields = []

    for field in fields:
        if field == r"\N":
            parsed_fields.append(None)
        else:
            parsed_fields.append(field)

    return parsed_fields
