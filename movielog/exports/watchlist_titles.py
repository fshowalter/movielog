from collections import defaultdict
from typing import Literal, TypedDict

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
        "releaseSequence": str,
        "directorNames": list[str],
        "performerNames": list[str],
        "writerNames": list[str],
        "collectionNames": list[str],
    },
)

WatchlistIndexKey = Literal[repository_api.WatchlistPersonKind, "collections"]

WachlistIndex = dict[str, dict[WatchlistIndexKey, list[str]]]


def append_name_if_not_reviewed(
    name: str,
    title_id: str,
    index: WachlistIndex,
    key: WatchlistIndexKey,
    repository_data: RepositoryData,
) -> None:
    if title_id not in repository_data.reviews.keys():
        index[title_id][key].append(name)


def build_watchlist_index(  # noqa: WPS210
    repository_data: RepositoryData,
) -> WachlistIndex:
    watchlist_index: WachlistIndex = defaultdict(lambda: defaultdict(list))

    for collection in repository_data.collections:
        for collection_title_id in collection.title_ids:
            append_name_if_not_reviewed(
                name=collection.name,
                title_id=collection_title_id,
                key="collections",
                index=watchlist_index,
                repository_data=repository_data,
            )

    for watchlist_key in repository_api.WATCHLIST_PERSON_KINDS:
        for watchlist_person in repository_data.watchlist[watchlist_key]:
            for title_id in watchlist_person.title_ids:
                append_name_if_not_reviewed(
                    name=watchlist_person.name,
                    title_id=title_id,
                    index=watchlist_index,
                    key=watchlist_key,
                    repository_data=repository_data,
                )

    return watchlist_index


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "watchlist-titles")

    watchlist_title_index = build_watchlist_index(repository_data=repository_data)

    watchlist_titles = []

    for watchlist_title_id in watchlist_title_index.keys():
        title = repository_data.titles[watchlist_title_id]

        watchlist_titles.append(
            JsonTitle(
                imdbId=title.imdb_id,
                title=title.title,
                year=title.year,
                sortTitle=title.sort_title,
                releaseSequence=title.release_sequence,
                directorNames=watchlist_title_index[title.imdb_id]["directors"],
                performerNames=watchlist_title_index[title.imdb_id]["performers"],
                writerNames=watchlist_title_index[title.imdb_id]["writers"],
                collectionNames=watchlist_title_index[title.imdb_id]["collections"],
            )
        )

    exporter.serialize_dicts(
        sorted(
            watchlist_titles,
            key=lambda watchlist_title: watchlist_title["releaseSequence"],
        ),
        "watchlist-titles",
    )
