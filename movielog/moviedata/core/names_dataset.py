from __future__ import annotations

from typing import Optional

from movielog.moviedata.core import downloader, extractor, movies_table, people_table
from movielog.utils import format_tools
from movielog.utils.logging import logger

NAMES_FILE_NAME = "name.basics.tsv.gz"

PeopleRow = people_table.Row


def valid_known_for_title_ids(all_known_for_title_ids: Optional[str]) -> Optional[str]:
    if not all_known_for_title_ids:
        return all_known_for_title_ids

    movie_ids = movies_table.movie_ids()

    known_for_title_ids = []

    for title_id in all_known_for_title_ids.split(","):
        if title_id in movie_ids:
            known_for_title_ids.append(title_id)

    return ",".join(known_for_title_ids)


def extract_names(file_path: str) -> list[PeopleRow]:
    names: dict[str, PeopleRow] = {}
    filtered = 0

    for fields in extractor.extract(file_path):
        known_for_title_ids = valid_known_for_title_ids(fields[5])

        if known_for_title_ids:
            imdb_id = str(fields[0])
            names[imdb_id] = people_table.Row(
                imdb_id=imdb_id,
                full_name=str(fields[1]),
                known_for_title_ids=known_for_title_ids,
            )
        else:
            filtered += 1

    logger.log("Extracted {} {}.", format_tools.humanize_int(len(names)), "names")
    logger.log(
        "Filtered {} {} with {}.",
        format_tools.humanize_int(filtered),
        "names",
        "no known-for titles",
    )

    return list(names.values())


def refresh() -> None:
    downloaded_file_path = downloader.download(NAMES_FILE_NAME)

    for _ in extractor.checkpoint(downloaded_file_path):  # noqa: WPS122
        names = extract_names(downloaded_file_path)
        people_table.reload(names)
