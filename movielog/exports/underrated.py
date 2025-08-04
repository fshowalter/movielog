from typing import TypedDict

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.utils.logging import logger


class JsonTitle(TypedDict):
    imdbId: str
    title: str
    releaseYear: str
    sortTitle: str
    reviewDate: str
    slug: str
    grade: str
    gradeValue: int
    genres: list[str]
    releaseSequence: str
    reviewSequence: str


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "underrated")

    imdb_low_rated_reviewed_title_ids = [
        title.imdb_id
        for title in repository_data.imdb_ratings.titles
        if (title.rating and title.votes)
        and title.rating < repository_data.imdb_ratings.average_imdb_rating
    ]

    underrated_surprises = []

    for imdb_id in imdb_low_rated_reviewed_title_ids:
        title = repository_data.titles[imdb_id]
        review = repository_data.reviews[title.imdb_id]
        viewings = sorted(
            [viewing for viewing in repository_data.viewings if viewing.imdb_id == title.imdb_id],
            key=lambda viewing: f"{viewing.date.isoformat()}-{viewing.sequence}",
            reverse=True,
        )

        if not review.grade_value or review.grade_value < 8:
            continue

        underrated_surprises.append(
            JsonTitle(
                imdbId=title.imdb_id,
                title=title.title,
                releaseYear=title.release_year,
                sortTitle=title.sort_title,
                slug=review.slug,
                grade=review.grade,
                gradeValue=review.grade_value,
                genres=title.genres,
                releaseSequence=title.release_sequence,
                reviewDate=review.date.isoformat(),
                reviewSequence="{}-{}".format(
                    review.date.isoformat(), viewings[0].sequence if viewings else ""
                ),
            )
        )

    exporter.serialize_dicts(
        sorted(
            underrated_surprises,
            key=lambda disappointment: "{}{}".format(
                disappointment["releaseYear"], disappointment["imdbId"]
            ),
            reverse=True,
        ),
        "underrated",
    )
