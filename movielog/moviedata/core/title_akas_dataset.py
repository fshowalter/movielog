from __future__ import annotations

from movielog.moviedata.core import (
    aka_titles_table,
    downloader,
    extractor,
    movies_table,
)
from movielog.utils import format_tools
from movielog.utils.logging import logger

TITLE_AKAS_FILE_NAME = "title.akas.tsv.gz"
TABLE_NAME = "aka_titles"


def extract_aka_titles(file_path: str) -> list[aka_titles_table.Row]:
    akas: list[aka_titles_table.Row] = []
    movie_imdb_ids = movies_table.movie_ids()

    for fields in extractor.extract(file_path):
        imdb_id = str(fields[0])

        if imdb_id in movie_imdb_ids:
            akas.append(
                aka_titles_table.Row(
                    movie_imdb_id=imdb_id,
                    sequence=int(str(fields[1])),
                    title=str(fields[2]),
                    region=fields[3],
                    language=fields[4],
                    types=fields[5],
                    attributes=fields[6],
                    is_original_title=(fields[7] == "1"),
                )
            )

    logger.log("Extracted {} {}.", format_tools.humanize_int(len(akas)), "aka titles")

    return akas


def refresh() -> None:
    downloaded_file_path = downloader.download(TITLE_AKAS_FILE_NAME)

    for _ in extractor.checkpoint(downloaded_file_path):  # noqa: WPS122
        rows = extract_aka_titles(downloaded_file_path)
        aka_titles_table.reload(rows)
