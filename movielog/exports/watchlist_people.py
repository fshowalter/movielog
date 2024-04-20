from typing import Optional, TypedDict

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils.logging import logger

JsonTitle = TypedDict(
    "JsonTitle",
    {
        "imdbId": str,
        "title": str,
        "sortTitle": str,
        "year": str,
        "slug": Optional[str],
        "grade": Optional[str],
        "gradeValue": Optional[int],
        "releaseSequence": str,
    },
)

JsonWatchlistPerson = TypedDict(
    "JsonWatchlistPerson",
    {
        "name": str,
        "slug": Optional[str],
        "titleCount": int,
        "reviewCount": int,
        "titles": list[JsonTitle],
    },
)


def build_watchlist_person_titles(
    watchlist_person: repository_api.WatchlistPerson, repository_data: RepositoryData
) -> list[JsonTitle]:
    titles = []
    for title_id in watchlist_person.title_ids:
        title = repository_data.titles[title_id]
        review = repository_data.reviews.get(title_id, None)

        titles.append(
            JsonTitle(
                imdbId=title_id,
                title=title.title,
                sortTitle=title.sort_title,
                year=title.year,
                releaseSequence=title.release_sequence,
                slug=review.slug if review else None,
                grade=review.grade if review else None,
                gradeValue=review.grade_value if review else None,
            )
        )

    return sorted(titles, key=lambda title: title["releaseSequence"])


def export(repository_data: RepositoryData) -> None:
    for kind in repository_api.WATCHLIST_PERSON_KINDS:
        logger.log("==== Begin exporting {}...", "watchlist-{0}".format(kind))

        watchlist_people = []

        for watchlist_person in repository_data.watchlist[kind]:
            reviewed_titles = [
                review
                for review in repository_data.reviews.values()
                if review.imdb_id in watchlist_person.title_ids
            ]

            watchlist_people.append(
                JsonWatchlistPerson(
                    name=watchlist_person.name,
                    slug=watchlist_person.slug if reviewed_titles else None,
                    titleCount=len(watchlist_person.title_ids),
                    reviewCount=len(reviewed_titles),
                    titles=build_watchlist_person_titles(
                        watchlist_person, repository_data
                    ),
                )
            )

        exporter.serialize_dicts(
            watchlist_people,
            "watchlist-{0}".format(kind),
        )
