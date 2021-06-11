import json
import os

from movielog.viewings import venues


def test_active_venues_returns_sorted_filtered_venues(tmp_path: str) -> None:

    expected = ["Alamo Drafthouse", "Blu-ray", "DVD"]

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
            "date": "2006-03-26",
            "imdb_id": "tt0266697",
            "title": "Kill Bill: Vol. 1 (2003)",
            "venue": "Alamo Drafthouse",
        },
        {
            "sequence": 3,
            "date": "2006-04-29",
            "imdb_id": "tt0025480",
            "title": "Bad Seed (1934)",
            "venue": "Arte",
        },
        {
            "sequence": 4,
            "date": "2007-03-26",
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

    assert expected == venues.active()
