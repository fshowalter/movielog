from movielog.watchlist_collection import Collection, Movie


def test_adds_title() -> None:
    collection = Collection(name="Hammer Films")
    expected = [
        Movie(imdb_id="tt0050280", title="The Curse of Frankenstein", year=1957)
    ]

    collection.add_title(
        imdb_id="tt0050280", title="The Curse of Frankenstein", year=1957
    )

    assert collection.movies == expected


def test_sorts_added_title_by_year() -> None:
    expected = [
        Movie(imdb_id="tt0050280", title="The Curse of Frankenstein", year=1957),
        Movie(imdb_id="tt0051554", title="Horror of Dracula", year=1958),
        Movie(imdb_id="tt0053085", title="The Mummy", year=1959),
    ]

    collection = Collection(
        name="Hammer Films",
        movies=[
            Movie(imdb_id="tt0050280", title="The Curse of Frankenstein", year=1957),
            Movie(imdb_id="tt0053085", title="The Mummy", year=1959),
        ],
    )

    collection.add_title(imdb_id="tt0051554", title="Horror of Dracula", year=1958)

    assert collection.movies == expected
