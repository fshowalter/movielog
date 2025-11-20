from __future__ import annotations

from pathlib import Path

from movielog.repository import format_tools
from movielog.repository.datasets import downloader, extractor
from movielog.repository.datasets.dataset_title import DatasetTitle as _DatasetTitle
from movielog.utils.logging import logger

TITLE_RATINGS_FILE_NAME = "title.ratings.tsv.gz"


DatasetTitle = _DatasetTitle


def _parse_imdb_rating(field: object) -> float:
    return float(str(field))


def _parse_imdb_votes(field: object) -> int:
    return int(str(field))


def extract_ratings(
    title_ratings_file_path: Path,
) -> list[DatasetTitle]:
    titles = [
        DatasetTitle(
            imdb_id=fields[0],
            imdb_rating=_parse_imdb_rating(fields[1]),
            imdb_votes=_parse_imdb_votes(fields[2]),
        )
        for fields in extractor.extract(title_ratings_file_path)
        if fields[0] and fields[1] and fields[2]
    ]

    logger.log(
        "Extracted {} {}.",
        format_tools.humanize_int(len(titles)),
        "title ratings",
    )

    return titles


def download_and_extract() -> list[DatasetTitle]:
    title_ratings_file_path = downloader.download(TITLE_RATINGS_FILE_NAME)

    return extract_ratings(title_ratings_file_path)
