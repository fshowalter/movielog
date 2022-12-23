from datetime import date
from typing import Callable

from movielog.reviews import api as reviews_api
from movielog.reviews import reviews_table
from tests.conftest import QueryResult


def test_update_reloads_table_with_given_entities(
    sql_query: Callable[[str], QueryResult]
) -> None:

    reviews = [
        reviews_api.create_or_update(
            review_date=date(2005, 3, 26),
            imdb_id="tt0159693",
            slug="razor-blade-smile-1998",
            grade="B",
        ),
        reviews_api.create_or_update(
            review_date=date(2006, 4, 29),
            imdb_id="tt0025480",
            slug="bad-seed-1934",
            grade="C",
        ),
        reviews_api.create_or_update(
            review_date=date(2007, 3, 29),
            imdb_id="tt0266697",
            slug="kill-bill-vol-1-2003",
            grade="B+",
        ),
        reviews_api.create_or_update(
            review_date=date(2008, 6, 29),
            imdb_id="tt0053221",
            slug="rio-bravo-1959",
            grade="A+",
        ),
    ]

    expected = [
        {
            "id": 1,
            "movie_imdb_id": "tt0159693",
            "date": "2005-03-26",
            "grade": "B",
            "grade_value": 9,
            "slug": "razor-blade-smile-1998",
        },
        {
            "id": 2,
            "movie_imdb_id": "tt0025480",
            "date": "2006-04-29",
            "grade": "C",
            "grade_value": 6,
            "slug": "bad-seed-1934",
        },
        {
            "id": 3,
            "movie_imdb_id": "tt0266697",
            "date": "2007-03-29",
            "grade": "B+",
            "grade_value": 10,
            "slug": "kill-bill-vol-1-2003",
        },
        {
            "id": 4,
            "movie_imdb_id": "tt0053221",
            "date": "2008-06-29",
            "grade": "A+",
            "grade_value": 13,
            "slug": "rio-bravo-1959",
        },
    ]

    reviews_table.update(reviews)

    assert expected == sql_query("SELECT * FROM 'reviews' order by id;")
