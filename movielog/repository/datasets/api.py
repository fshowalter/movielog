from __future__ import annotations

from pathlib import Path

from movielog.repository import format_tools
from movielog.repository.datasets import downloader, extractor
from movielog.repository.datasets.dataset_name import DatasetName as _DatasetName
from movielog.repository.datasets.dataset_title import DatasetTitle as _DatasetTitle
from movielog.utils.logging import logger

TITLE_BASICS_FILE_NAME = "title.basics.tsv.gz"
NAME_BASICS_FILE_NAME = "name.basics.tsv.gz"
TITLE_RATINGS_FILE_NAME = "title.ratings.tsv.gz"
TITLE_PRINCIPALS_FILE_NAME = "title.principals.tsv.gz"
TITLE_AKAS_FILE_NAME = "title.akas.tsv.gz"

AllowList = {
    "tt0148615",  # Play Motel (1979) [X]
    "tt0070696",  # The Sinful Dwarf (1973) [X]
    "tt0839995",  # Superman II: The Richard Donner Cut [no principal cast -- all "archive footage"]
    "tt0024005",  # Fast Workers (Tod Browning director - uncredited)
    "tt0027521",  # The Devil Doll (Tod Browning director - uncredited)
}

DatasetName = _DatasetName
DatasetTitle = _DatasetTitle


def title_fields_are_valid(fields: extractor.DatasetFields) -> bool:
    if fields[1] not in {"movie", "video", "tvMovie"}:
        return False
    if fields[4] == "1":  # adult
        return False
    if fields[5] is None:  # no year
        return False
    if fields[7] is None:  # no runtime
        return False
    if int(fields[7]) < 40:  # less than 40 minutes
        return False

    return "Documentary" not in (fields[8] or "")


def extract_titles(title_basics_file_path: Path) -> dict[str, DatasetTitle]:
    titles: dict[str, DatasetTitle] = {}

    for fields in extractor.extract(title_basics_file_path):
        imdb_id = str(fields[0])
        if imdb_id in AllowList or title_fields_are_valid(fields):
            title = str(fields[2])
            year = str(fields[5] or "????")
            titles[imdb_id] = DatasetTitle(
                imdb_id=str(fields[0]),
                title=title,
                original_title=str(fields[3]),
                full_title=f"{title} ({year})",
                year=year,
                runtime_minutes=int(str(fields[7])),
                principal_cast=[],
                aka_titles=[],
                imdb_votes=None,
                imdb_rating=None,
            )

    logger.log("Extracted {} {}.", format_tools.humanize_int(len(titles)), "titles")

    return titles


def update_titles_with_principals(
    title_principals_file_path: Path,
    titles: dict[str, DatasetTitle],
    names: dict[str, DatasetName],
) -> None:
    count = 0
    for fields in extractor.extract(title_principals_file_path):
        title = titles.get(str(fields[0]), None)
        if not title or fields[3] not in {"actor", "actress"}:
            continue

        name = names.get(str(fields[2]), None)
        if not name:
            continue

        title["principal_cast"].append(name["full_name"])
        count += 1

    logger.log(
        "Extracted {} {}.",
        format_tools.humanize_int(count),
        "principals",
    )


def parse_imdb_rating(field: object) -> float | None:
    if not field:
        return None

    return float(str(field))


def parse_imdb_votes(field: object) -> int | None:
    if not field:
        return None

    return int(str(field))


def update_titles_with_ratings(
    title_ratings_file_path: Path,
    titles: dict[str, DatasetTitle],
) -> None:
    count = 0
    for fields in extractor.extract(title_ratings_file_path):
        title = titles.get(str(fields[0]), None)
        if not title:
            continue

        title["imdb_rating"] = parse_imdb_rating(fields[1])
        title["imdb_votes"] = parse_imdb_votes(fields[2])
        count += 1

    logger.log(
        "Extracted {} {}.",
        format_tools.humanize_int(count),
        "title ratings",
    )


def prune_titles_with_no_principal_cast(
    titles: dict[str, DatasetTitle],
) -> None:
    removed = 0

    for title in list(titles.values()):
        if not title["principal_cast"] and title["imdb_id"] not in AllowList:
            del titles[title["imdb_id"]]
            removed += 1

    logger.log(
        "Filtered {} {} with {}.",
        format_tools.humanize_int(removed),
        "titles",
        "no principal cast",
    )


def extract_names(file_path: Path, titles: dict[str, DatasetTitle]) -> dict[str, DatasetName]:
    names: dict[str, DatasetName] = {}

    for fields in extractor.extract(file_path):
        imdb_id = str(fields[0])
        names[imdb_id] = DatasetName(
            imdb_id=imdb_id,
            full_name=str(fields[1]),
            known_for_titles=[
                titles[known_for_title_id]["full_title"]
                for known_for_title_id in (fields[5] or "").split(",")
                if known_for_title_id in titles
            ],
        )

    logger.log("Extracted {} {}.", format_tools.humanize_int(len(names)), "names")

    return names


def aka_title_is_not_for_usa_or_great_britain(field: object) -> bool:
    return str(field) not in {"US", "GB"}


def update_titles_with_akas(file_path: Path, titles: dict[str, DatasetTitle]) -> None:
    count = 0

    for fields in extractor.extract(file_path):
        title = titles.get(str(fields[0]), None)

        if not title:
            continue

        if aka_title_is_not_for_usa_or_great_britain(fields[3]):
            continue

        aka_title = str(fields[2])

        if aka_title in {title["title"], title["original_title"]}:
            continue

        title["aka_titles"].append(aka_title)

        count += 1

    logger.log("Extracted {} {}.", format_tools.humanize_int(count), "aka titles")


def download_and_extract() -> tuple[dict[str, DatasetTitle], dict[str, DatasetName]]:
    title_basics_file_path = downloader.download(TITLE_BASICS_FILE_NAME)
    title_principals_file_path = downloader.download(TITLE_PRINCIPALS_FILE_NAME)
    title_ratings_file_path = downloader.download(TITLE_RATINGS_FILE_NAME)
    title_akas_file_path = downloader.download(TITLE_AKAS_FILE_NAME)
    name_basics_file_path = downloader.download(NAME_BASICS_FILE_NAME)

    titles = extract_titles(title_basics_file_path)
    update_titles_with_ratings(title_ratings_file_path, titles)
    update_titles_with_akas(title_akas_file_path, titles)
    names = extract_names(name_basics_file_path, titles)
    update_titles_with_principals(title_principals_file_path, titles, names)
    prune_titles_with_no_principal_cast(titles)

    return (titles, names)
