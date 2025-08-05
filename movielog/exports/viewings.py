from movielog.exports import exporter
from movielog.exports.json_viewed_title import JsonViewedTitle
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils.logging import logger


def build_json_viewing(
    viewing: repository_api.Viewing, sequence: int, repository_data: RepositoryData
) -> JsonViewedTitle:
    title = repository_data.titles[viewing.imdb_id]
    review = repository_data.reviews.get(viewing.imdb_id, None)

    viewings = sorted(
        [v for v in repository_data.viewings if v.imdb_id == viewing.imdb_id],
        key=lambda v: f"{v.date.isoformat()}-{v.sequence}",
        reverse=True,
    )

    return JsonViewedTitle(
        # JsonTitle fields
        imdbId=viewing.imdb_id,
        title=title.title,
        releaseYear=title.release_year,
        sortTitle=title.sort_title,
        releaseSequence=title.release_sequence,
        genres=title.genres,
        # JsonMaybeReviewedTitle fields
        slug=review.slug if review else None,
        grade=review.grade if review else None,
        gradeValue=review.grade_value if review else None,
        reviewDate=review.date.isoformat() if review else None,
        reviewSequence=(
            f"{review.date.isoformat()}-{viewings[0].sequence}" if viewings and review else None
        ),
        # JsonViewedTitle fields
        viewingDate=viewing.date.isoformat(),
        viewingSequence=sequence,
        medium=viewing.medium,
        venue=viewing.venue,
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
