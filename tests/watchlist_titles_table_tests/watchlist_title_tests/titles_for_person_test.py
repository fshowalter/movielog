from movielog.watchlist_file import Title
from movielog.watchlist_person import Director, Performer, Writer
from movielog.watchlist_titles_table import WatchlistTitle


def test_builds_titles_for_director() -> None:
    expected = [
        WatchlistTitle(movie_imdb_id="test_movie_1", director_imdb_id="director_id"),
        WatchlistTitle(movie_imdb_id="test_movie_2", director_imdb_id="director_id"),
        WatchlistTitle(movie_imdb_id="test_movie_3", director_imdb_id="director_id"),
    ]

    person = Director(
        file_path=None, name="Test Director", imdb_id="director_id", titles=None
    )

    person.titles.extend(
        [
            Title(imdb_id="test_movie_1", title="Test Movie 1", year=1959),
            Title(imdb_id="test_movie_2", title="Test Movie 2", year=1976),
            Title(imdb_id="test_movie_3", title="Test Movie 3", year=1984),
        ]
    )

    assert expected == WatchlistTitle.titles_for_person(person)


def test_builds_titles_for_performer() -> None:
    expected = [
        WatchlistTitle(movie_imdb_id="test_movie_1", performer_imdb_id="performer_id"),
        WatchlistTitle(movie_imdb_id="test_movie_2", performer_imdb_id="performer_id"),
        WatchlistTitle(movie_imdb_id="test_movie_3", performer_imdb_id="performer_id"),
    ]

    person = Performer(
        file_path=None, name="Test Performer", imdb_id="performer_id", titles=None
    )

    person.titles.extend(
        [
            Title(imdb_id="test_movie_1", title="Test Movie 1", year=1959),
            Title(imdb_id="test_movie_2", title="Test Movie 2", year=1976),
            Title(imdb_id="test_movie_3", title="Test Movie 3", year=1984),
        ]
    )

    assert expected == WatchlistTitle.titles_for_person(person)


def test_builds_titles_for_writer() -> None:
    expected = [
        WatchlistTitle(movie_imdb_id="test_movie_1", writer_imdb_id="writer_id"),
        WatchlistTitle(movie_imdb_id="test_movie_2", writer_imdb_id="writer_id"),
        WatchlistTitle(movie_imdb_id="test_movie_3", writer_imdb_id="writer_id"),
    ]

    person = Writer(
        file_path=None, name="Test Writer", imdb_id="writer_id", titles=None
    )

    person.titles.extend(
        [
            Title(imdb_id="test_movie_1", title="Test Movie 1", year=1959),
            Title(imdb_id="test_movie_2", title="Test Movie 2", year=1976),
            Title(imdb_id="test_movie_3", title="Test Movie 3", year=1984),
        ]
    )

    assert expected == WatchlistTitle.titles_for_person(person)
