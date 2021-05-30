from typing import Callable, Optional, Sequence, TypedDict

from movielog.moviedata.core import downloader, extractor, movies_table
from movielog.utils import format_tools
from movielog.utils.logging import logger

TITLE_AKAS_FILE_NAME = "title.akas.tsv.gz"
TABLE_NAME = "aka_titles"


class Aka(TypedDict):
    movie_imdb_id: str
    title: str
    sequence: int
    region: Optional[str]
    language: Optional[str]
    types: Optional[str]
    attributes: Optional[str]
    is_original_title: bool


def extract_aka_titles(file_path: str) -> list[Aka]:
    akas: list[Aka] = []
    movie_imdb_ids = movies_table.movie_ids()

    for fields in extractor.extract(file_path):
        imdb_id = str(fields[0])

        if imdb_id in movie_imdb_ids:
            akas.append(
                Aka(
                    movie_imdb_id=imdb_id,
                    sequence=int(str(fields[1])),
                    title=str(fields[2]),
                    region=fields[3],
                    language=fields[4],
                    types=fields[5],
                    attributes=fields[6],
                    is_original_title=bool(fields[7]),
                )
            )

    logger.log("Extracted {} {}.", format_tools.humanize_int(len(akas)), "aka titles")

    return akas


def refresh(callback: Callable[[Sequence[Aka]], None]) -> None:
    downloaded_file_path = downloader.download(TITLE_AKAS_FILE_NAME)

    for _ in extractor.checkpoint(downloaded_file_path):  # noqa: WPS122
        akas = extract_aka_titles(downloaded_file_path)
        callback(akas)
