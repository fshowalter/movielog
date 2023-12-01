from dataclasses import dataclass

from movielog.repository import api as repository_api

Watchlist = dict[
    repository_api.WatchlistEntityKind, list[repository_api.WatchlistEntity]
]


@dataclass
class RepositoryData(object):
    viewings: list[repository_api.Viewing]
    titles: list[repository_api.Title]
    reviews: list[repository_api.Review]
    reviewed_titles: list[repository_api.Title]
    watchlist: Watchlist
    review_ids: set[str]
