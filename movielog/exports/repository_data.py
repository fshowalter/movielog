from dataclasses import dataclass
from typing import Literal

from movielog.repository import api as repository_api

WatchlistTitlesKey = Literal[repository_api.WatchlistPersonKind, "collections"]

WachlistTitles = dict[str, dict[WatchlistTitlesKey, list[str]]]

WatchlistPeople = dict[
    repository_api.WatchlistPersonKind, list[repository_api.WatchlistPerson]
]


@dataclass
class RepositoryData:
    viewings: list[repository_api.Viewing]
    titles: dict[str, repository_api.Title]
    reviews: dict[str, repository_api.Review]
    reviewed_titles: list[repository_api.Title]
    watchlist_people: WatchlistPeople
    watchlist_titles: WachlistTitles
    collections: list[repository_api.Collection]
    imdb_ratings: repository_api.ImdbRatings
    cast_and_crew: dict[frozenset[str], repository_api.CastAndCrewMember]
