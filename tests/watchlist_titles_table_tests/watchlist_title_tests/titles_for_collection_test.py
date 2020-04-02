from movielog.watchlist_collection import Collection
from movielog.watchlist_file import Title
from movielog.watchlist_titles_table import WatchlistTitle


def test_builds_titles_for_collection() -> None:
    expected = [
        WatchlistTitle(movie_imdb_id="test_movie_1", collection_name="Test Collection"),
        WatchlistTitle(movie_imdb_id="test_movie_2", collection_name="Test Collection"),
        WatchlistTitle(movie_imdb_id="test_movie_3", collection_name="Test Collection"),
    ]

    collection = Collection(
        file_path=None, name="Test Collection", imdb_id=None, titles=None
    )

    collection.titles.extend(
        [
            Title(imdb_id="test_movie_1", title="Test Movie 1", year=1959),
            Title(imdb_id="test_movie_2", title="Test Movie 2", year=1976),
            Title(imdb_id="test_movie_3", title="Test Movie 3", year=1984),
        ]
    )

    assert expected == WatchlistTitle.titles_for_collection(collection)
