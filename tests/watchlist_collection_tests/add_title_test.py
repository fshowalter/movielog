from movielog.watchlist_collection import Collection
from movielog.watchlist_file import Title


def test_adds_title() -> None:
    collection = Collection(name="Hammer Films")
    expected = [
        Title(imdb_id="tt0050280", title="The Curse of Frankenstein", year=1957)
    ]

    collection.add_title(
        imdb_id="tt0050280", title="The Curse of Frankenstein", year=1957
    )

    assert collection.titles == expected


def test_sorts_added_title_by_year() -> None:
    expected = [
        Title(imdb_id="tt0050280", title="The Curse of Frankenstein", year=1957),
        Title(imdb_id="tt0051554", title="Horror of Dracula", year=1958),
        Title(imdb_id="tt0053085", title="The Mummy", year=1959),
    ]

    collection = Collection(
        name="Hammer Films",
        titles=[
            Title(imdb_id="tt0050280", title="The Curse of Frankenstein", year=1957),
            Title(imdb_id="tt0053085", title="The Mummy", year=1959),
        ],
    )

    collection.add_title(imdb_id="tt0051554", title="Horror of Dracula", year=1958)

    assert collection.titles == expected
