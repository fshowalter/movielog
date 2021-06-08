from datetime import date

import pytest

from movielog.reviews.review import Review


@pytest.mark.parametrize(
    "grade, expected_grade_value",
    [
        ("A+", 5.33),
        ("A", 5.0),
        ("A-", 4.67),
        ("B+", 4.33),
        ("B", 4.0),
        ("B-", 3.67),
        ("C+", 3.33),
        ("C", 3.0),
        ("C-", 2.67),
        ("D+", 2.33),
        ("D", 2.0),
        ("D-", 1.67),
        ("F", 1.0),
    ],
)
def test_grade_value_accounts_for_modifers(
    grade: str, expected_grade_value: float
) -> None:
    review = Review(
        sequence=1,
        grade=grade,
        imdb_id="tt0053221",
        title="Rio Bravo",
        date=date(2017, 3, 12),
        venue="Alamo Drafthouse",
        slug="rio-bravo-1959",
    )

    assert review.grade_value == expected_grade_value
