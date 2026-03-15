from typing import TypedDict

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.utils.logging import logger


class _JsonWatchlistTitle(TypedDict):
    imdbId: str
    title: str
    sortTitle: str
    releaseYear: str
    releaseDate: str
    genres: list[str]
    watchlistDirectorNames: list[str]
    watchlistPerformerNames: list[str]
    watchlistWriterNames: list[str]
    watchlistCollectionNames: list[str]


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "watchlist-titles")

    watchlist_titles = []

    for watchlist_title_id in repository_data.watchlist_titles:
        title = repository_data.titles[watchlist_title_id]

        watchlist_titles.append(
            _JsonWatchlistTitle(
                imdbId=title.imdb_id,
                title=title.title,
                releaseYear=title.release_year,
                sortTitle=title.sort_title,
                releaseDate=title.release_date,
                genres=title.genres,
                watchlistDirectorNames=repository_data.watchlist_titles[title.imdb_id]["directors"],
                watchlistPerformerNames=repository_data.watchlist_titles[title.imdb_id][
                    "performers"
                ],
                watchlistWriterNames=repository_data.watchlist_titles[title.imdb_id]["writers"],
                watchlistCollectionNames=repository_data.watchlist_titles[title.imdb_id][
                    "collections"
                ],
            )
        )

    exporter.serialize_dicts(
        sorted(
            watchlist_titles,
            key=lambda watchlist_title: watchlist_title["imdbId"],
        ),
        "watchlist-titles",
    )
