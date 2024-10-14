from typing import TypedDict

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.utils.logging import logger

JsonTitle = TypedDict(
    "JsonTitle",
    {
        "imdbId": str,
        "title": str,
        "year": str,
        "sortTitle": str,
        "slug": str,
        "grade": str,
        "gradeValue": int,
        "genres": list[str],
        "releaseSequence": str,
    },
)

GRADE_VALUE_A = 12


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "best-of-the-best")

    best_of_the_best = []

    for reviewed_title in repository_data.reviewed_titles:
        review = repository_data.reviews[reviewed_title.imdb_id]

        if review.grade_value < GRADE_VALUE_A:
            continue

        viewings = [
            viewing
            for viewing in repository_data.viewings
            if viewing.imdb_id == reviewed_title.imdb_id
        ]

        if len(viewings) < 3:
            continue

        best_of_the_best.append(
            JsonTitle(
                imdbId=reviewed_title.imdb_id,
                title=reviewed_title.title,
                year=reviewed_title.year,
                sortTitle=reviewed_title.sort_title,
                slug=review.slug,
                grade=review.grade,
                gradeValue=review.grade_value,
                genres=reviewed_title.genres,
                releaseSequence=reviewed_title.release_sequence,
            )
        )

    exporter.serialize_dicts(
        sorted(
            best_of_the_best,
            key=lambda gem: "{0}{1}".format(gem["year"], gem["imdbId"]),
            reverse=True,
        ),
        "best-of-the-best",
    )
