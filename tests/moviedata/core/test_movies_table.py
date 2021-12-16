from movielog.moviedata.core import movies_table


def test_reload_clears_ids_cache() -> None:
    movies_table.reload([])

    assert movies_table.movie_ids() == set()

    movies_table.reload(
        [
            movies_table.Row(
                imdb_id="tt0051554",
                title="Horror of Dracula",
                original_title="Dracula",
                year=1958,
                runtime_minutes=None,
                principal_cast_ids=None,
                votes=23,
                imdb_rating=6,
            ),
            movies_table.Row(
                imdb_id="tt0053221",
                title="Rio Bravo",
                original_title="Rio Bravo",
                year=1959,
                runtime_minutes=None,
                principal_cast_ids=None,
                votes=23,
                imdb_rating=8,
            ),
            movies_table.Row(
                imdb_id="tt0089175",
                title="Fright Night",
                original_title="Fright Night",
                year=1985,
                runtime_minutes=None,
                principal_cast_ids=None,
                votes=23,
                imdb_rating=6.1,
            ),
        ]
    )

    expected = set(["tt0051554", "tt0053221", "tt0089175"])

    assert movies_table.movie_ids() == expected
