"""Shared utility functions for export modules."""

from typing import overload

from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api


@overload
def calculate_review_sequence(
    imdb_id: str,
    review: repository_api.Review,
    repository_data: RepositoryData,
) -> int: ...


@overload
def calculate_review_sequence(
    imdb_id: str,
    review: repository_api.Review | None,
    repository_data: RepositoryData,
) -> int | None: ...


def calculate_review_sequence(
    imdb_id: str,
    review: repository_api.Review | None,
    repository_data: RepositoryData,
) -> int | None:
    """Get the review sequence number for a title.

    Returns None if there's no review, otherwise returns the integer
    sequence number from the pre-calculated review sequence map.
    """
    if not review:
        return None

    return repository_data.review_sequence_map.get(imdb_id)


def calculate_release_sequence(
    imdb_id: str,
    repository_data: RepositoryData,
) -> int:
    """Get the release sequence number for a title.

    Returns the integer sequence number from the pre-calculated release sequence map.
    """
    sequence = repository_data.release_sequence_map.get(imdb_id)
    if sequence is None:
        raise ValueError(f"No release sequence found for title {imdb_id}")
    return sequence


def calculate_title_sequence(
    imdb_id: str,
    repository_data: RepositoryData,
) -> int:
    """Get the title sequence number for a title.

    Returns the integer sequence number from the pre-calculated title sequence map.
    """
    sequence = repository_data.title_sequence_map.get(imdb_id)
    if sequence is None:
        raise ValueError(f"No title sequence found for title {imdb_id}")
    return sequence


@overload
def calculate_grade_sequence(
    imdb_id: str,
    review: repository_api.Review,
    repository_data: RepositoryData,
) -> int: ...


@overload
def calculate_grade_sequence(
    imdb_id: str,
    review: repository_api.Review | None,
    repository_data: RepositoryData,
) -> int | None: ...


def calculate_grade_sequence(
    imdb_id: str,
    review: repository_api.Review | None,
    repository_data: RepositoryData,
) -> int | None:
    """Get the grade sequence number for a reviewed title.

    Returns None if there's no review, otherwise returns the integer
    sequence number from the pre-calculated grade sequence map.
    """
    if not review:
        return None

    return repository_data.grade_sequence_map.get(imdb_id)


def calculate_viewing_sequence(
    imdb_id: str,
    viewing_sequence: int,
    repository_data: RepositoryData,
) -> int:
    """Get the viewing sequence number for a specific viewing.

    Returns the integer sequence number from the pre-calculated viewing sequence map.
    """
    sequence = repository_data.viewing_sequence_map.get((imdb_id, viewing_sequence))
    if sequence is None:
        raise ValueError(f"No viewing sequence found for viewing {imdb_id}-{viewing_sequence}")
    return sequence
