from datetime import date, timedelta

from movielog.reviews import api as reviews_api
from movielog.reviews import venues


def test_recent_venues_returns_recent_venues(tmp_path: str) -> None:

    expected = ["Alamo Drafthouse", "Blu-ray"]

    reviews_api.create(
        review_date=date(2005, 3, 26),
        imdb_id="tt0159693",
        title="Razor Blade Smile",
        year=1998,
        grade="B",
        venue="DVD",
    )

    reviews_api.create(
        review_date=date(2006, 4, 29),
        imdb_id="tt0025480",
        title="Bad Seed",
        year=1934,
        grade="C",
        venue="Arte",
    )

    reviews_api.create(
        review_date=(date.today() - timedelta(days=1)),
        imdb_id="tt0266697",
        title="Kill Bill: Vol. 1",
        year=2003,
        grade="B+",
        venue="Alamo Drafthouse",
    )

    reviews_api.create(
        review_date=date.today(),
        imdb_id="tt0053221",
        title="Rio Bravo",
        year=1959,
        grade="A+",
        venue="Blu-ray",
    )

    assert expected == venues.recent()
