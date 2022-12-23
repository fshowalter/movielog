from datetime import date

import pytest

from movielog.reviews.review import Review


@pytest.mark.parametrize(
    "grade, expected_grade_value",
    [
        ("A+", 13),
        ("A", 12),
        ("A-", 11),
        ("B+", 10),
        ("B", 9),
        ("B-", 8),
        ("C+", 7),
        ("C", 6),
        ("C-", 5),
        ("D+", 4),
        ("D", 3),
        ("D-", 2),
        ("F", 1),
    ],
)
def test_grade_value_accounts_for_modifers(
    grade: str, expected_grade_value: float
) -> None:
    review = Review(
        grade=grade,
        imdb_id="tt0053221",
        date=date(2017, 3, 12),
        slug="rio-bravo-1959",
    )

    assert review.grade_value == expected_grade_value
