from movielog.exports import exporter
from movielog.exports.json_title import JsonTitle
from movielog.exports.json_watchlist_fields import JsonWatchlistFields
from movielog.exports.repository_data import RepositoryData
from movielog.utils.logging import logger


class JsonWatchlistTitle(JsonTitle, JsonWatchlistFields):
    viewed: bool


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "watchlist-titles")

    watchlist_titles = []

    viewing_imdb_ids = {viewing.imdb_id for viewing in repository_data.viewings}

    for watchlist_title_id in repository_data.watchlist_titles:
        title = repository_data.titles[watchlist_title_id]

        watchlist_titles.append(
            JsonWatchlistTitle(
                imdbId=title.imdb_id,
                title=title.title,
                releaseYear=title.release_year,
                sortTitle=title.sort_title,
                releaseSequence=title.release_sequence,
                genres=title.genres,
                watchlistDirectorNames=repository_data.watchlist_titles[title.imdb_id]["directors"],
                watchlistPerformerNames=repository_data.watchlist_titles[title.imdb_id][
                    "performers"
                ],
                watchlistWriterNames=repository_data.watchlist_titles[title.imdb_id]["writers"],
                watchlistCollectionNames=repository_data.watchlist_titles[title.imdb_id][
                    "collections"
                ],
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
