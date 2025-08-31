from movielog.exports import exporter
from movielog.exports.json_viewed_title import JsonViewedTitle
from movielog.exports.repository_data import RepositoryData
from movielog.exports.utils import (
    calculate_grade_sequence,
    calculate_release_sequence,
    calculate_review_sequence,
    calculate_viewing_sequence,
)
from movielog.repository import api as repository_api
from movielog.utils.logging import logger


def build_json_viewing(
    viewing: repository_api.Viewing, repository_data: RepositoryData
) -> JsonViewedTitle:
    title = repository_data.titles[viewing.imdb_id]
    review = repository_data.reviews.get(viewing.imdb_id, None)

    return JsonViewedTitle(
        # JsonTitle fields
        imdbId=viewing.imdb_id,
        title=title.title,
        sortTitle=title.sort_title,
        releaseYear=title.release_year,
        releaseSequence=calculate_release_sequence(title.imdb_id, repository_data),
        genres=title.genres,
        # JsonMaybeReviewedTitle fields
        slug=review.slug if review else None,
        grade=review.grade if review else None,
        gradeValue=review.grade_value if review else None,
        gradeSequence=calculate_grade_sequence(viewing.imdb_id, review, repository_data),
        reviewDate=review.date.isoformat() if review else None,
        reviewSequence=calculate_review_sequence(viewing.imdb_id, review, repository_data),
        # JsonViewedTitle fields
        viewingDate=viewing.date.isoformat(),
        viewingSequence=calculate_viewing_sequence(
            viewing.imdb_id, viewing.sequence, repository_data
        ),
        medium=viewing.medium,
        venue=viewing.venue,
    )


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "viewings")

    json_viewings = [
        build_json_viewing(viewing=viewing, repository_data=repository_data)
        for viewing in repository_data.viewings
    ]

    exporter.serialize_dicts(
        json_viewings,
        "viewings",
    )
