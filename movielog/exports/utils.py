"""Shared utility functions for export modules."""

from typing import overload

from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api


@overload
def calculate_review_sequence(
    imdb_id: str,
    review: repository_api.Review,
    repository_data: RepositoryData,
) -> str: ...


@overload
def calculate_review_sequence(
    imdb_id: str,
    review: repository_api.Review | None,
    repository_data: RepositoryData,
) -> str | None: ...


def calculate_review_sequence(
    imdb_id: str,
    review: repository_api.Review | None,
    repository_data: RepositoryData,
) -> str | None:
    """Calculate review sequence for deterministic sorting by review date.

    Uses the most recent viewing's sequence to ensure unique ordering
    when multiple titles are reviewed on the same date.

    Returns None if there's no review, otherwise returns the review date
    combined with the most recent viewing's sequence.
    """
    if not review:
        return None

    viewings = sorted(
        [v for v in repository_data.viewings if v.imdb_id == imdb_id],
        key=lambda v: f"{v.date.isoformat()}-{v.sequence}",
        reverse=True,
    )

    if not viewings:
        # This should never happen - a review must have at least one viewing
        raise ValueError(f"No viewings found for reviewed title {imdb_id}")

    # Use the sequence of the most recent viewing
    return f"{review.date.isoformat()}-{viewings[0].sequence}"
