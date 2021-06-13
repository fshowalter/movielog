from datetime import date
from typing import Callable

from movielog.reviews import viewings_table
from movielog.reviews.viewings import Viewing
from tests.conftest import QueryResult


def test_update_reloads_table_with_given_entities(
    sql_query: Callable[[str], QueryResult]
) -> None:

    viewings = [
        Viewing(
            sequence=1,
            date=date(2005, 3, 26),
            imdb_id="tt0159693",
            title="Razor Blade Smile (1998)",
            venue="DVD",
        ),
        Viewing(
            sequence=2,
            date=date(2006, 4, 29),
            imdb_id="tt0025480",
            title="Bad Seed (1934)",
            venue="Arte",
        ),
        Viewing(
            sequence=3,
            date=date(2007, 5, 15),
            imdb_id="tt0266697",
            title="Kill Bill: Vol. 1 (2003)",
            venue="Alamo Drafthouse",
        ),
        Viewing(
            sequence=4,
            date=date(2008, 2, 5),
            imdb_id="tt0053221",
            title="Rio Bravo (1959)",
            venue="Blu-ray",
        ),
    ]

    expected = [
        {
            "id": 1,
            "sequence": 1,
            "date": "2005-03-26",
            "movie_imdb_id": "tt0159693",
            "venue": "DVD",
        },
        {
            "id": 2,
            "sequence": 2,
            "date": "2006-04-29",
            "movie_imdb_id": "tt0025480",
            "venue": "Arte",
        },
        {
            "id": 3,
            "sequence": 3,
            "date": "2007-05-15",
            "movie_imdb_id": "tt0266697",
            "venue": "Alamo Drafthouse",
        },
        {
            "id": 4,
            "sequence": 4,
            "date": "2008-02-05",
            "movie_imdb_id": "tt0053221",
            "venue": "Blu-ray",
        },
    ]

    viewings_table.update(viewings)

    assert expected == sql_query("SELECT * FROM 'viewings' order by sequence;")
