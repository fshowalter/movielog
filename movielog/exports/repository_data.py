from dataclasses import dataclass

from movielog.repository import api as repository_api


@dataclass
class RepositoryData:
    viewings: list[repository_api.Viewing]
    titles: dict[str, repository_api.Title]
    reviews: dict[str, repository_api.Review]
    reviewed_titles: list[repository_api.Title]
    watchlist_people: dict[
        repository_api.WatchlistPersonKind, list[repository_api.WatchlistPerson]
    ]
    watchlist_collections: list[repository_api.WatchlistCollection]
    metadata: repository_api.Metadata
    names: list[repository_api.Name]
