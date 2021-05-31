import json
import os

from pytest_mock import MockerFixture

from movielog import viewings


def test_returns_venues_sorted(tmp_path: str, mocker: MockerFixture) -> None:
    mocker.patch("movielog.viewings.FOLDER_PATH", tmp_path)

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
            "sequence": 2,
            "date": "2007-03-26",
            "imdb_id": "tt0053221",
            "title": "Rio Bravo (1959)",
            "venue": "Blu-ray",
        },
    ]

    for index, existing_viewing in enumerate(existing_viewings):
        with open(os.path.join(tmp_path, f"viewing-{index}.json"), "w") as output_file:
            output_file.write(json.dumps(existing_viewing))

    assert viewings.venues() == expected
