from typing import TypedDict

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.utils.logging import logger


class JsonTitle(TypedDict):
    imdbId: str
    title: str
    year: str
    sortTitle: str
    slug: str
    grade: str
    gradeValue: int
    genres: list[str]
    releaseSequence: str


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

        if not review.grade_value or review.grade_value < 8:
            continue

        underseen_gems.append(
            JsonTitle(
                imdbId=title.imdb_id,
                title=title.title,
                year=title.year,
                sortTitle=title.sort_title,
                slug=review.slug,
                grade=review.grade,
                gradeValue=review.grade_value,
                genres=title.genres,
                releaseSequence=title.release_sequence,
            )
        )

    exporter.serialize_dicts(
        sorted(
            underseen_gems,
            key=lambda gem: "{0}{1}".format(gem["year"], gem["imdbId"]),
            reverse=True,
        ),
        "underseen",
    )
