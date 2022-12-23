import json
import os
from datetime import date

from movielog.viewings import serializer
from movielog.viewings.viewing import Viewing


def test_deserialize_all_deserializes_viewings(tmp_path: str) -> None:

    expected = [
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

    existing_viewings = [
        {
            "sequence": 1,
            "date": "2005-03-26",
            "imdb_id": "tt0159693",
            "medium": "DVD",
            "slug": "razor-blade-smile-1998",
            "venue": None,
            "medium_notes": None,
        },
        {
            "sequence": 2,
            "date": "2006-04-29",
            "imdb_id": "tt0025480",
            "medium": "Arte",
            "slug": "bad-seed-1934",
            "venue": None,
            "medium_notes": None,
        },
        {
            "sequence": 3,
            "date": "2007-05-15",
            "imdb_id": "tt0266697",
            "medium": "Blu-ray",
            "slug": "kill-bill-vol-1-2003",
            "venue": None,
            "medium_notes": None,
        },
        {
            "sequence": 4,
            "date": "2008-02-05",
            "imdb_id": "tt0053221",
            "medium": "Blu-ray",
            "slug": "rio-bravo-1959",
            "venue": None,
            "medium_notes": None,
        },
    ]

    for index, existing_viewing in enumerate(existing_viewings):
        with open(
            os.path.join(tmp_path, "viewing_{0}.json".format(index)), "w"
        ) as output_file:
            output_file.write(json.dumps(existing_viewing))

    assert serializer.deserialize_all() == expected
