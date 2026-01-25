from __future__ import annotations

from collections import defaultdict

from movielog.exports import (
    cast_and_crew,
    collections,
    overrated,
    reviewed_titles,
    stats,
    underrated,
    underseen,
    viewings,
    watchlist_progress,
    watchlist_titles,
)
from movielog.exports.repository_data import (
    RepositoryData,
    WachlistTitles,
    WatchlistPeople,
    WatchlistTitlesKey,
)
from movielog.repository import api as repository_api
from movielog.utils import list_tools
from movielog.utils.logging import logger


def _build_watchlist_people() -> WatchlistPeople:
    watchlist = {}

    for watchlist_key in repository_api.WATCHLIST_PERSON_KINDS:
        watchlist[watchlist_key] = sorted(
            repository_api.watchlist_people(kind=watchlist_key),
            key=lambda entity: entity.slug,
        )

    return watchlist


def _append_name_if_not_reviewed(
    name: str,
    title_id: str,
    index: WachlistTitles,
    key: WatchlistTitlesKey,
    reviews: dict[str, repository_api.Review],
) -> None:
    if title_id not in reviews:
        index[title_id][key].append(name)


def _build_watchlist_titles(
    watchlist_people: WatchlistPeople,
    reviews: dict[str, repository_api.Review],
) -> WachlistTitles:
    watchlist_title_index: WachlistTitles = defaultdict(lambda: defaultdict(list))

    for collection in repository_api.collections():
        for collection_title_id in collection.title_ids:
            _append_name_if_not_reviewed(
                name=collection.name,
                title_id=collection_title_id,
                key="collections",
                index=watchlist_title_index,
                reviews=reviews,
            )

    for watchlist_key in repository_api.WATCHLIST_PERSON_KINDS:
        for watchlist_person in watchlist_people[watchlist_key]:
            for title_id in watchlist_person.title_ids:
                _append_name_if_not_reviewed(
                    name=watchlist_person.name,
                    title_id=title_id,
                    index=watchlist_title_index,
                    key=watchlist_key,
                    reviews=reviews,
                )

    return watchlist_title_index


def export_data(token: str) -> None:
    logger.log("Initializing...")

    repository_api.validate_data(token)

    reviews = list_tools.list_to_dict(repository_api.reviews(), key=lambda review: review.imdb_id)

    titles = list_tools.list_to_dict(repository_api.titles(), key=lambda title: title.imdb_id)

    cast_and_crew_by_imdb_id = list_tools.list_to_dict(
        repository_api.cast_and_crew(), key=lambda member: member.imdb_id
    )

    watchlist_people = _build_watchlist_people()

    repository_data = RepositoryData(
        viewings=sorted(
            repository_api.viewings(),
            key=lambda viewing: f"{viewing.date}{viewing.sequence}",
        ),
        titles=titles,
        reviews=reviews,
        reviewed_titles=[titles[review_id] for review_id in reviews],
        watchlist_people=watchlist_people,
        watchlist_titles=_build_watchlist_titles(watchlist_people, reviews),
        collections=sorted(
            repository_api.collections(),
            key=lambda collection: collection.slug,
        ),
        imdb_ratings=repository_api.imdb_ratings(),
        cast_and_crew=cast_and_crew_by_imdb_id,
    )

    viewings.export(repository_data)
    reviewed_titles.export(repository_data)
    underrated.export(repository_data)
    overrated.export(repository_data)
    underseen.export(repository_data)
    watchlist_titles.export(repository_data)
    collections.export(repository_data)
    stats.export(repository_data)
    watchlist_progress.export(repository_data)
    cast_and_crew.export(repository_data)
