from movielog.watchlist_file import Title


def test_returns_as_object() -> None:
    expected = {
        "title": "Rio Bravo",
        "imdb_id": "tt0053221",
        "year": 1959,
    }

    title = Title(imdb_id="tt0053221", title="Rio Bravo", year=1959, notes="")

    assert title.as_yaml() == expected


def test_if_notes_adds_notes() -> None:
    expected = {
        "title": "Rio Bravo",
        "notes": "Best.Movie.Ever.",
        "imdb_id": "tt0053221",
        "year": 1959,
    }

    title = Title(
        imdb_id="tt0053221", title="Rio Bravo", year=1959, notes="Best.Movie.Ever."
    )

    assert title.as_yaml() == expected
