from typing import TypedDict

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.utils.logging import logger


class JsonTitle(TypedDict):
    imdbId: str
    title: str
    year: str
    sortTitle: str
    releaseSequence: str
    directorNames: list[str]
    performerNames: list[str]
    writerNames: list[str]
    collectionNames: list[str]
    viewed: bool


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "watchlist-titles")

    watchlist_titles = []

    viewing_imdb_ids = set(viewing.imdb_id for viewing in repository_data.viewings)

    for watchlist_title_id in repository_data.watchlist_titles.keys():
        title = repository_data.titles[watchlist_title_id]

        watchlist_titles.append(
            JsonTitle(
                imdbId=title.imdb_id,
                title=title.title,
                year=title.year,
                sortTitle=title.sort_title,
                releaseSequence=title.release_sequence,
                directorNames=repository_data.watchlist_titles[title.imdb_id]["directors"],
                performerNames=repository_data.watchlist_titles[title.imdb_id]["performers"],
                writerNames=repository_data.watchlist_titles[title.imdb_id]["writers"],
                collectionNames=repository_data.watchlist_titles[title.imdb_id]["collections"],
                viewed=title.imdb_id in viewing_imdb_ids,
            )
        )

    exporter.serialize_dicts(
        sorted(
            watchlist_titles,
            key=lambda watchlist_title: watchlist_title["releaseSequence"],
        ),
        "watchlist-titles",
    )
