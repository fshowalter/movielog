from typing import TypedDict

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils.logging import logger


class JsonViewing(TypedDict):
    sequence: int
    viewingYear: str
    viewingDate: str
    title: str
    sortTitle: str
    releaseSequence: str
    medium: str | None
    venue: str | None
    year: str
    slug: str | None
    genres: list[str]


def build_json_viewing(
    viewing: repository_api.Viewing, sequence: int, repository_data: RepositoryData
) -> JsonViewing:
    title = repository_data.titles[viewing.imdb_id]
    review = repository_data.reviews.get(viewing.imdb_id, None)

    return JsonViewing(
        sequence=sequence,
        viewingYear=str(viewing.date.year),
        viewingDate=viewing.date.isoformat(),
        title=title.title,
        sortTitle=title.sort_title,
        medium=viewing.medium,
        venue=viewing.venue,
        year=title.year,
        slug=review.slug if review else None,
        genres=title.genres,
        releaseSequence=title.release_sequence,
    )


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "viewings")

    json_viewings = [
        build_json_viewing(viewing=viewing, sequence=index + 1, repository_data=repository_data)
        for index, viewing in enumerate(repository_data.viewings)
    ]

    exporter.serialize_dicts(
        json_viewings,
        "viewings",
    )
