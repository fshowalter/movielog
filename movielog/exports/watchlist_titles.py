from collections import defaultdict
from typing import Literal, Optional, TypedDict

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils.logging import logger

JsonTitle = TypedDict(
    "JsonTitle",
    {
        "imdbId": str,
        "title": str,
        "year": str,
        "sortTitle": str,
        "slug": Optional[str],
        "grade": Optional[str],
        "gradeValue": Optional[int],
        "directorNames": list[str],
        "performerNames": list[str],
        "writerNames": list[str],
        "collectionNames": list[str],
    },
)

WachlistIndex = dict[
    str, dict[Literal[repository_api.WatchlistPersonKind, "collections"], list[str]]
]


def build_watchlist_index(repository_data: RepositoryData) -> WachlistIndex:
    watchlist_index: WachlistIndex = defaultdict(lambda: defaultdict(list))

    for collection in repository_data.watchlist_collections:
        for collection_title_id in collection.title_ids:
            watchlist_index[collection_title_id]["collections"].append(collection.name)

    for watchlist_key in repository_api.WATCHLIST_PERSON_KINDS:
        for watchlist_person in repository_data.watchlist_people[watchlist_key]:
            for title_id in watchlist_person.title_ids:
                watchlist_index[title_id][watchlist_key].append(watchlist_person.name)

    return watchlist_index


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "watchlist-titles")

    watchlist_title_index = build_watchlist_index(repository_data=repository_data)

    watchlist_titles = []

    for watchlist_title_id in watchlist_title_index.keys():
        title = repository_data.titles[watchlist_title_id]
        review = repository_data.reviews.get(watchlist_title_id, None)

        watchlist_titles.append(
            JsonTitle(
                imdbId=title.imdb_id,
                title=title.title,
                year=title.year,
                sortTitle=title.sort_title,
                slug=review.slug if review else None,
                grade=review.grade if review else None,
                gradeValue=review.grade_value if review else None,
                directorNames=watchlist_title_index[title.imdb_id]["directors"],
                performerNames=watchlist_title_index[title.imdb_id]["performers"],
                writerNames=watchlist_title_index[title.imdb_id]["writers"],
                collectionNames=watchlist_title_index[title.imdb_id]["collections"],
            )
        )

    exporter.serialize_dicts_to_folder(
        watchlist_titles,
        "watchlist-titles",
        filename_key=lambda watchlist_title: watchlist_title["imdbId"],
    )
