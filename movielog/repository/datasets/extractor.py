import gzip
from collections.abc import Generator, Sequence

from movielog.utils.logging import logger

DatasetFields = list[str | None]


def extract(
    file_path: str,
) -> Generator[DatasetFields]:
    logger.log("Begin extracting from {}...", file_path)

    with gzip.open(filename=file_path, mode="rt", encoding="utf-8") as gz_file:
        headers_length = len(gz_file.readline().strip().split("\t"))
        for line in gz_file:
            fields: Sequence[str | None] = line.strip().split("\t")
            if len(fields) != headers_length:
                continue

            yield parse_fields(fields)


def parse_fields(
    fields: Sequence[str | None],
) -> DatasetFields:
    parsed_fields: DatasetFields = []

    for field in fields:
        if field == r"\N":
            parsed_fields.append(None)
        else:
            parsed_fields.append(field)

    return parsed_fields
