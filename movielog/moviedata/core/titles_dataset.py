from collections import defaultdict
from typing import Callable, Dict, Optional, Sequence, TypedDict

from movielog.moviedata.core import downloader, extractor
from movielog.utils import format_tools
from movielog.utils.logging import logger

TITLE_BASICS_FILE_NAME = "title.basics.tsv.gz"
TITLE_PRINCIPALS_FILE_NAME = "title.principals.tsv.gz"

Whitelist = {
    "tt0019035",  # Interference (1928) (no runtime)
    "tt0116671",  # Jack Frost (1997) [V]
    "tt0148615",  # Play Motel (1979) [X]
    "tt1801096",  # Sexy Evil Genius (2013) [V]
    "tt0093135",  # Hack-O-Lantern (1988) [V]
    "tt11060882",  # Batman: The Dark Knight Returns (2013) [V]
    "tt0101760",  # Door to Silence (1992) [V]
}


class Title(TypedDict):
    imdb_id: str
    title: str
    original_title: str
    year: str
    runtime_minutes: Optional[int]
    principal_cast_ids: Optional[str]


class Principal(TypedDict):
    imdb_id: str
    order: int


def title_fields_are_valid(fields: extractor.DatasetFields) -> bool:  # noqa: WPS212
    if fields[1] != "movie":
        return False
    if fields[4] == "1":
        return False
    if fields[5] is None:
        return False
    if fields[7] is None:
        return False

    genres = set(str(fields[8]).split(","))

    return "Documentary" not in genres


def extract_titles(title_basics_file_path: str) -> Dict[str, Title]:
    titles: Dict[str, Title] = {}

    for fields in extractor.extract(title_basics_file_path):
        imdb_id = str(fields[0])
        if imdb_id in Whitelist or title_fields_are_valid(fields):
            titles[imdb_id] = Title(
                imdb_id=str(fields[0]),
                title=str(fields[2]),
                original_title=str(fields[3]),
                year=str(fields[5]),
                runtime_minutes=int(str(fields[7])) if fields[7] else None,
                principal_cast_ids=None,
            )

    logger.log("Extracted {} {}.", format_tools.humanize_int(len(titles)), "titles")

    return titles


def extract_principals(
    titles: Dict[str, Title], title_principals_file_path: str
) -> Dict[str, list[Principal]]:
    principals = defaultdict(list)

    for fields in extractor.extract(title_principals_file_path):
        movie_imdb_id = str(fields[0])
        if movie_imdb_id not in titles:
            continue
        if fields[3] not in {"actor", "actress"}:
            continue

        order = int(str(fields[1])) if fields[1] else 0
        principal = Principal(imdb_id=str(fields[2]), order=order)

        principals[movie_imdb_id].append(principal)

    logger.log(
        "Extracted {} {}.",
        format_tools.humanize_int(len(principals)),
        "title cast principals",
    )

    return principals


def append_principal_cast_ids(
    titles: Dict[str, Title], principals: Dict[str, list[Principal]]
) -> list[Title]:
    removed = 0

    for imdb_id in list(titles.keys()):
        principals_for_imdb_id = principals[imdb_id]
        if principals_for_imdb_id:
            sorted_principals = sorted(
                principals_for_imdb_id, key=lambda princ: princ["order"]
            )
            titles[imdb_id]["principal_cast_ids"] = ",".join(
                map(lambda princ: princ["imdb_id"], sorted_principals)
            )
        else:
            del titles[imdb_id]  # noqa: WPS420
            removed += 1

    logger.log(
        "Filtered {} {} with {}.",
        format_tools.humanize_int(removed),
        "titles",
        "no principal cast",
    )

    return list(titles.values())


def refresh(callback: Callable[[Sequence[Title]], None]) -> None:
    title_basics_file_path = downloader.download(TITLE_BASICS_FILE_NAME)
    title_principals_file_path = downloader.download(TITLE_PRINCIPALS_FILE_NAME)

    for _ in extractor.checkpoint(title_principals_file_path):  # noqa: WPS122
        titles = extract_titles(title_basics_file_path)
        principals = extract_principals(titles, title_principals_file_path)
        titles_with_principal_cast_ids = append_principal_cast_ids(titles, principals)
        callback(titles_with_principal_cast_ids)
