from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
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
        if not review.grade_value or review.grade_value < 12:
            continue

        underrated_surprises.append(review.slug)

    exporter.serialize_dict(
        {"titles": sorted(underrated_surprises)},
        "underrated",
    )
