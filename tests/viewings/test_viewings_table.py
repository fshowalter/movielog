from datetime import date
from typing import Callable

from movielog.viewings import viewings_table
from movielog.viewings.viewing import Viewing
from tests.conftest import QueryResult


def test_update_reloads_table_with_given_entities(
    sql_query: Callable[[str], QueryResult]
) -> None:

    viewings = [
        Viewing(
            sequence=1,
            date=date(2005, 3, 26),
            imdb_id="tt0159693",
            slug="razor-blade-smile-1998",
            medium="DVD",
        ),
        Viewing(
            sequence=2,
            date=date(2006, 4, 29),
            imdb_id="tt0025480",
            slug="bad-seed-1934",
            medium="Arte",
        ),
        Viewing(
            sequence=3,
            date=date(2007, 5, 15),
            imdb_id="tt0266697",
            slug="kill-bill-vol-1-2003",
            medium="Blu-ray",
        ),
        Viewing(
            sequence=4,
            date=date(2008, 2, 5),
            imdb_id="tt0053221",
            slug="rio-bravo-1959",
            medium="Blu-ray",
        ),
    ]

    expected = [
        {
            "id": 1,
            "sequence": 1,
            "date": "2005-03-26",
            "movie_imdb_id": "tt0159693",
            "medium": "DVD",
            "venue": None,
            "medium_notes": None,
        },
        {
            "id": 2,
            "sequence": 2,
            "date": "2006-04-29",
            "movie_imdb_id": "tt0025480",
            "medium": "Arte",
            "venue": None,
            "medium_notes": None,
        },
        {
            "id": 3,
            "sequence": 3,
            "date": "2007-05-15",
            "movie_imdb_id": "tt0266697",
            "medium": "Blu-ray",
            "venue": None,
            "medium_notes": None,
        },
        {
            "id": 4,
            "sequence": 4,
            "date": "2008-02-05",
            "movie_imdb_id": "tt0053221",
            "medium": "Blu-ray",
            "venue": None,
            "medium_notes": None,
        },
    ]

    viewings_table.update(viewings)

    assert expected == sql_query("SELECT * FROM 'viewings' order by sequence;")
