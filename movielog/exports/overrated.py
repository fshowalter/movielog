from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.utils.logging import logger


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "overrated")

    imdb_high_rated_reviewed_title_ids = [
        title.imdb_id
        for title in repository_data.imdb_ratings.titles
        if (title.rating and title.votes)
        and title.rating > repository_data.imdb_ratings.average_imdb_rating
    ]

    overrated_disappointments = []

    for imdb_id in imdb_high_rated_reviewed_title_ids:
        title = repository_data.titles[imdb_id]
        review = repository_data.reviews[title.imdb_id]
        if not review.grade_value or review.grade_value > 7:
            continue

        overrated_disappointments.append(review.slug)

    exporter.serialize_dict(
        {"titles": sorted(overrated_disappointments)},
        "overrated",
    )
