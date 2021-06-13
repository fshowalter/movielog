from datetime import date
from typing import Callable

from movielog.reviews import api as reviews_api
from movielog.reviews import reviews_table
from tests.conftest import QueryResult


def test_update_reloads_table_with_given_entities(
    sql_query: Callable[[str], QueryResult]
) -> None:

    reviews = [
        reviews_api.create(
            review_date=date(2005, 3, 26),
            imdb_id="tt0159693",
            title="Razor Blade Smile",
            year=1998,
            grade="B",
            venue="DVD",
        ),
        reviews_api.create(
            review_date=date(2006, 4, 29),
            imdb_id="tt0025480",
            title="Bad Seed",
            year=1934,
            grade="C",
            venue="Arte",
        ),
        reviews_api.create(
            review_date=date(2007, 3, 29),
            imdb_id="tt0266697",
            title="Kill Bill: Vol. 1",
            year=2003,
            grade="B+",
            venue="Alamo Drafthouse",
        ),
        reviews_api.create(
            review_date=date(2008, 6, 29),
            imdb_id="tt0053221",
            title="Rio Bravo",
            year=1959,
            grade="A+",
            venue="Blu-ray",
        ),
    ]

    expected = [
        {
            "id": 1,
            "sequence": 1,
            "movie_imdb_id": "tt0159693",
            "date": "2005-03-26",
            "grade": "B",
            "grade_value": 4,
            "slug": "razor-blade-smile-1998",
            "venue": "DVD",
        },
        {
            "id": 2,
            "sequence": 2,
            "movie_imdb_id": "tt0025480",
            "date": "2006-04-29",
            "grade": "C",
            "grade_value": 3,
            "slug": "bad-seed-1934",
            "venue": "Arte",
        },
        {
            "id": 3,
            "sequence": 3,
            "movie_imdb_id": "tt0266697",
            "date": "2007-03-29",
            "grade": "B+",
            "grade_value": 4.33,
            "slug": "kill-bill-vol-1-2003",
            "venue": "Alamo Drafthouse",
        },
        {
            "id": 4,
            "sequence": 4,
            "movie_imdb_id": "tt0053221",
            "date": "2008-06-29",
            "grade": "A+",
            "grade_value": 5.33,
            "slug": "rio-bravo-1959",
            "venue": "Blu-ray",
        },
    ]

    reviews_table.update(reviews)

    assert expected == sql_query("SELECT * FROM 'reviews' order by sequence;")
