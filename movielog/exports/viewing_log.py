import datetime
from typing import TypedDict

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils.list_tools import group_list_by_key
from movielog.utils.logging import logger


class _JsonViewingLogEntry(TypedDict):
    title: str
    sortTitle: str
    releaseYear: str
    releaseDate: str
    genres: list[str]
    reviewSlug: str | None
    date: datetime.date
    sequence: str
    medium: str | None
    venue: str | None


def build_json_viewing(
    viewing: repository_api.Viewing, repository_data: RepositoryData
) -> _JsonViewingLogEntry:
    title = repository_data.titles[viewing.imdb_id]
    review = repository_data.reviews.get(viewing.imdb_id, None)

    return _JsonViewingLogEntry(
        title=title.title,
        sortTitle=title.sort_title,
        releaseYear=title.release_year,
        releaseDate=title.release_date,
        genres=title.genres,
        reviewSlug=review.slug if review else None,
        date=viewing.date,
        sequence=f"{viewing.date.isoformat()}-{viewing.sequence:02}",
        medium=viewing.medium,
        venue=viewing.venue,
    )


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "viewing-log")

    json_viewings = [
        build_json_viewing(viewing=viewing, repository_data=repository_data)
        for viewing in repository_data.viewings
    ]

    grouped_entries = group_list_by_key(
        json_viewings, lambda entry: f"{entry['date'].year}-{entry['date'].month:02}"
    )

    for year_month, entries in grouped_entries.items():
        exporter.serialize_dicts_to_file(
            dicts=sorted(entries, key=lambda entry: entry["sequence"]),
            folder_name="viewing-log",
            file_name=year_month,
        )
