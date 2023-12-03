from typing import Optional, TypedDict

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils.logging import logger

JsonViewing = TypedDict(
    "JsonViewing",
    {
        "sequence": int,
        "viewingYear": str,
        "viewingDate": str,
        "title": str,
        "sortTitle": str,
        "medium": Optional[str],
        "venue": Optional[str],
        "year": str,
        "slug": Optional[str],
        "genres": list[str],
    },
)


def build_json_viewing(
    viewing: repository_api.Viewing, repository_data: RepositoryData
) -> JsonViewing:
    title = repository_data.titles[viewing.imdb_id]
    review = repository_data.reviews.get(viewing.imdb_id, None)

    return JsonViewing(
        sequence=viewing.sequence,
        viewingYear=str(viewing.date.year),
        viewingDate=viewing.date.isoformat(),
        title=title.title,
        sortTitle=title.sort_title,
        medium=viewing.medium,
        venue=viewing.venue,
        year=title.year,
        slug=review.slug if review else None,
        genres=title.genres,
    )


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "viewings")

    json_viewings = [
        build_json_viewing(viewing=viewing, repository_data=repository_data)
        for viewing in repository_data.viewings
    ]

    exporter.serialize_dicts_by_key(
        json_viewings,
        "viewings",
        key=lambda viewing: viewing["viewingYear"],
    )
