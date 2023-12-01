from dataclasses import dataclass

from movielog.repository import api as repository_api

WatchlistDict = dict[
    repository_api.WatchlistEntityKind, list[repository_api.WatchlistEntity]
]


@dataclass
class RepositoryData(object):
    viewings: list[repository_api.Viewing]
    viewings_for_id: dict[str, list[repository_api.Viewing]]
    titles: dict[str, repository_api.Title]
    reviews: dict[str, repository_api.Review]
    reviewed_titles: list[repository_api.Title]
    watchlist: WatchlistDict
    review_ids: set[str]
