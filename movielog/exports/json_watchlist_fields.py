from typing import TypedDict


class JsonWatchlistFields(TypedDict):
    """Fields for watchlist attribution (who/what added the title to watchlist)."""

    watchlistDirectorNames: list[str]
    watchlistPerformerNames: list[str]
    watchlistWriterNames: list[str]
    watchlistCollectionNames: list[str]
