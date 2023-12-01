from typing import Optional, TypedDict

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils.logging import logger

JsonViewing = TypedDict(
    "JsonViewing",
    {
        "viewingDate": str,
        "venue": Optional[str],
        "medium": Optional[str],
        "mediumNotes": Optional[str],
        "sequence": int,
    },
)

JsonReviewedTitle = TypedDict(
    "JsonReviewedTitle",
    {
        "imdbId": str,
        "title": str,
        "year": str,
        "slug": str,
        "grade": str,
        "countries": list[str],
        "genres": list[str],
        "releaseDate": str,
        "sortTitle": str,
        "originalTitle": str,
        "gradeValue": Optional[int],
        "runtimeMinutes": int,
        "directorNames": list[str],
        "principalCastNames": list[str],
        "reviewDate": str,
        "reviewYear": str,
        "viewings": list[JsonViewing],
    },
)


def build_json_reviewed_title(
    title: repository_api.Title,
    review: repository_api.Review,
    repository_data: RepositoryData,
) -> JsonReviewedTitle:
    return JsonReviewedTitle(
        imdbId=title.imdb_id,
        title=title.title,
        year=title.year,
        slug=review.slug,
        grade=review.grade,
        countries=title.countries,
        genres=title.genres,
        releaseDate=title.release_date.isoformat(),
        sortTitle=title.sort_title,
        originalTitle=title.original_title,
        gradeValue=review.grade_value,
        runtimeMinutes=title.runtime_minutes,
        directorNames=title.director_names,
        principalCastNames=title.principal_cast_names,
        reviewDate=review.date.isoformat(),
        reviewYear=str(review.date.year),
        viewings=[
            JsonViewing(
                sequence=viewing.sequence,
                medium=viewing.medium,
                mediumNotes=viewing.medium_notes,
                viewingDate=viewing.viewing_date.isoformat(),
                venue=viewing.venue,
            )
            for viewing in title.viewings(repository_data.viewings)
        ],
    )


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "reviewed-titles")

    json_reviewed_titles = []

    for title in repository_data.titles:
        review = title.review(repository_data.reviews)
        if not review:
            continue

        json_reviewed_titles.append(
            build_json_reviewed_title(
                title=title, review=review, repository_data=repository_data
            )
        )

    exporter.serialize_dicts_to_folder(
        json_reviewed_titles,
        "reviewed-titles",
        filename_key=lambda reviewed_title: reviewed_title["slug"],
    )
