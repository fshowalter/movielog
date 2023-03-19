from __future__ import annotations

from collections import defaultdict
from typing import Dict, Optional, TypedDict

from movielog.moviedata.core import downloader, extractor, movies_table
from movielog.utils import format_tools
from movielog.utils.logging import logger

TITLE_BASICS_FILE_NAME = "title.basics.tsv.gz"
TITLE_PRINCIPALS_FILE_NAME = "title.principals.tsv.gz"
TITLE_RATINGS_FILE_NAME = "title.ratings.tsv.gz"


Whitelist = {
    "tt0019035",  # Interference (1928) (no runtime)
    "tt0116671",  # Jack Frost (1997) [V]
    "tt0148615",  # Play Motel (1979) [X]
    "tt1801096",  # Sexy Evil Genius (2013) [V]
    "tt0093135",  # Hack-O-Lantern (1988) [V]
    "tt11060882",  # Batman: The Dark Knight Returns (2013) [V]
    "tt0101760",  # Door to Silence (1992) [V]
    "tt0112643",  # Castle Freak (1995) [V]
    "tt1356864",  # I'm Still Here (2010) (documentary)
    "tt0209095",  # Leprechaun 5: In the Hood [V]
    "tt0239496",  # Jack Frost 2 (2000) [V]
    "tt0094762",  # Blood Delerium (1988) (no year)
    "tt0113636",  # Leprechaun 3 [V]
}

MovieRow = movies_table.Row


class Principal(TypedDict):
    imdb_id: str
    order: int


class Rating(TypedDict):
    rating: Optional[float]
    votes: Optional[int]


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


def extract_titles(title_basics_file_path: str) -> Dict[str, MovieRow]:
    titles: Dict[str, MovieRow] = {}

    for fields in extractor.extract(title_basics_file_path):
        imdb_id = str(fields[0])
        if imdb_id in Whitelist or title_fields_are_valid(fields):
            titles[imdb_id] = movies_table.Row(
                imdb_id=str(fields[0]),
                title=str(fields[2]),
                original_title=str(fields[3]),
                year=int(str(fields[5] or "2023")),
                runtime_minutes=int(str(fields[7])) if fields[7] else None,
                principal_cast_ids=None,
                votes=None,
                imdb_rating=None,
            )

    logger.log("Extracted {} {}.", format_tools.humanize_int(len(titles)), "titles")

    return titles


def extract_principals(
    titles: Dict[str, MovieRow], title_principals_file_path: str
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


def extract_ratings(
    titles: Dict[str, MovieRow], title_ratings_file_path: str
) -> Dict[str, Rating]:
    votes: Dict[str, Rating] = defaultdict(lambda: Rating(rating=None, votes=None))

    for fields in extractor.extract(title_ratings_file_path):
        movie_imdb_id = str(fields[0])
        if movie_imdb_id not in titles:
            continue

        rating = float(str(fields[1])) if fields[1] else None
        number_of_votes = int(str(fields[2])) if fields[2] else None
        votes[movie_imdb_id] = Rating(rating=rating, votes=number_of_votes)

    logger.log(
        "Extracted {} {}.",
        format_tools.humanize_int(len(votes)),
        "title rating votes",
    )

    return votes


def append_principal_cast_ids_and_rating(
    titles: Dict[str, MovieRow],
    principals: Dict[str, list[Principal]],
    ratings: Dict[str, Rating],
) -> list[MovieRow]:
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
            rating = ratings[imdb_id]
            titles[imdb_id]["votes"] = rating["votes"]
            titles[imdb_id]["imdb_rating"] = rating["rating"]
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


def refresh() -> None:  # noqa: WPS210
    title_basics_file_path = downloader.download(TITLE_BASICS_FILE_NAME)
    title_principals_file_path = downloader.download(TITLE_PRINCIPALS_FILE_NAME)
    title_ratings_file_path = downloader.download(TITLE_RATINGS_FILE_NAME)

    for _ in extractor.checkpoint(title_principals_file_path):  # noqa: WPS122
        titles = extract_titles(title_basics_file_path)
        principals = extract_principals(titles, title_principals_file_path)
        ratings = extract_ratings(titles, title_ratings_file_path)
        titles_with_principal_cast_ids_and_votes = append_principal_cast_ids_and_rating(
            titles, principals, ratings
        )
        movies_table.reload(titles_with_principal_cast_ids_and_votes)
