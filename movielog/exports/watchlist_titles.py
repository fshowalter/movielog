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
        "year": str,
        "releaseDate": str,
        "sortTitle": str,
        "slug": Optional[str],
        "grade": Optional[str],
        "gradeValue": Optional[int],
        "directorName": list[str],
        "performerNames": list[str],
        "writerNames": list[str],
        "collectionNames": list[str],
    },
)


def build_json_title(
    viewing: repository_api.Viewing, repository_data: RepositoryData
) -> JsonTitle:
    title = viewing.title(repository_data.titles)
    review = title.review(repository_data.reviews)

    return JsonTitle(
        sequence=viewing.sequence,
        viewingYear=str(viewing.date.year),
        viewingDate=viewing.date.isoformat(),
        releaseDate=title.release_date.isoformat(),
        title=title.title,
        sortTitle=title.sort_title,
        medium=viewing.medium,
        venue=viewing.venue,
        year=title.year,
        slug=review.slug if review else None,
        genres=title.genres,
    )


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "watchlist-titles")

    json_viewings = [
        build_json_title(viewing=viewing, repository_data=repository_data)
        for viewing in repository_data.viewings
    ]

    exporter.serialize_dicts(json_viewings, "watchlist-titles")
