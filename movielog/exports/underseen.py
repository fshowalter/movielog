from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.utils.logging import logger


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "underseen")

    imdb_underseen_reviewed_title_ids = [
        title.imdb_id
        for title in repository_data.imdb_ratings.titles
        if title.votes and title.votes < repository_data.imdb_ratings.average_imdb_votes
    ]

    underseen_gems = []

    for imdb_id in imdb_underseen_reviewed_title_ids:
        title = repository_data.titles[imdb_id]
        review = repository_data.reviews[title.imdb_id]

        if not review.grade_value or review.grade_value < 12:
            continue

        underseen_gems.append(review.slug)

    exporter.serialize_dict(
        {"titles": sorted(underseen_gems)},
        "underseen",
    )
