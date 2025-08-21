from movielog.exports import exporter
from movielog.exports.json_reviewed_title import JsonReviewedTitle
from movielog.exports.repository_data import RepositoryData
from movielog.exports.utils import (
    calculate_grade_sequence,
    calculate_release_sequence,
    calculate_review_sequence,
    calculate_title_sequence,
)
from movielog.utils.logging import logger


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
        if not review.grade_value or review.grade_value < 8:
            continue

        underrated_surprises.append(
            JsonReviewedTitle(
                imdbId=title.imdb_id,
                title=title.title,
                releaseYear=title.release_year,
                titleSequence=calculate_title_sequence(title.imdb_id, repository_data),
                slug=review.slug,
                grade=review.grade,
                gradeValue=review.grade_value,
                gradeSequence=calculate_grade_sequence(title.imdb_id, review, repository_data),
                genres=title.genres,
                releaseSequence=calculate_release_sequence(title.imdb_id, repository_data),
                reviewDate=review.date.isoformat(),
                reviewSequence=calculate_review_sequence(title.imdb_id, review, repository_data),
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
