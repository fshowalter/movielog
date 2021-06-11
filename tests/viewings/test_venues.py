import json
import os
from datetime import date, timedelta

from movielog.viewings import venues


def test_active_venues_returns_recent_venues(tmp_path: str) -> None:

    expected = ["Alamo Drafthouse", "Blu-ray"]

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
            "date": (date.today() - timedelta(days=1)).isoformat(),
            "imdb_id": "tt0266697",
            "title": "Kill Bill: Vol. 1 (2003)",
            "venue": "Alamo Drafthouse",
        },
        {
            "sequence": 4,
            "date": date.today().isoformat(),
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

    assert expected == venues.recent()
