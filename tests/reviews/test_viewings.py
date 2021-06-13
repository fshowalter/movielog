import json
import os
from datetime import date

from movielog.reviews import viewings


def test_deserialize_all_deserizes_venues(tmp_path: str) -> None:

    expected = [
        viewings.Viewing(
            sequence=1,
            date=date(2005, 3, 26),
            imdb_id="tt0159693",
            title="Razor Blade Smile (1998)",
            venue="DVD",
        ),
        viewings.Viewing(
            sequence=2,
            date=date(2006, 4, 29),
            imdb_id="tt0025480",
            title="Bad Seed (1934)",
            venue="Arte",
        ),
        viewings.Viewing(
            sequence=3,
            date=date(2007, 5, 15),
            imdb_id="tt0266697",
            title="Kill Bill: Vol. 1 (2003)",
            venue="Alamo Drafthouse",
        ),
        viewings.Viewing(
            sequence=4,
            date=date(2008, 2, 5),
            imdb_id="tt0053221",
            title="Rio Bravo (1959)",
            venue="Blu-ray",
        ),
    ]

    existing_viewings = [
        {
            "sequence": 1,
            "date": "2005-03-26",
            "imdb_id": "tt0159693",
            "title": "Razor Blade Smile (1998)",
            "venue": "DVD",
        },
        {
            "sequence": 2,
            "date": "2006-04-29",
            "imdb_id": "tt0025480",
            "title": "Bad Seed (1934)",
            "venue": "Arte",
        },
        {
            "sequence": 3,
            "date": "2007-05-15",
            "imdb_id": "tt0266697",
            "title": "Kill Bill: Vol. 1 (2003)",
            "venue": "Alamo Drafthouse",
        },
        {
            "sequence": 4,
            "date": "2008-02-05",
            "imdb_id": "tt0053221",
            "title": "Rio Bravo (1959)",
            "venue": "Blu-ray",
        },
    ]

    for index, existing_viewing in enumerate(existing_viewings):
        with open(
            os.path.join(tmp_path, "viewing-{0}.json".format(index)), "w"
        ) as output_file:
            output_file.write(json.dumps(existing_viewing))

    assert viewings.deserialize_all() == expected
