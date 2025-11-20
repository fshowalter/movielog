from typing import TypedDict

from movielog.repository.json_watchlist_titles import JsonWatchlistTitle


class JsonWatchlistPerson(TypedDict):
    name: str
    slug: str
    imdbId: str | list[str]
    titles: list[JsonWatchlistTitle]
    excludedTitles: list[JsonWatchlistTitle]
