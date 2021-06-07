from datetime import date

import imdb

from movielog.moviedata.extended import release_dates


def test_parse_returns_empty_release_date_if_no_raw_release_dates() -> None:
    movie = imdb.Movie.Movie(data={"year": 2001})

    expected = release_dates.ReleaseDate(date=date(2001, 1, 1), notes="No release date")

    assert expected == release_dates.parse(movie)


def test_parse_returns_empty_release_date_if_raw_release_dates_malformed() -> None:
    movie = imdb.Movie.Movie(
        data={"year": 2001, "raw release dates": [{"bad_json": 2001}]}
    )

    expected = release_dates.ReleaseDate(date=date(2001, 1, 1), notes="No release date")

    assert expected == release_dates.parse(movie)
