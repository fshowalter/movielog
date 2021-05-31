import json
import os
from datetime import date

import pytest

from movielog.utils.sequence_tools import SequenceError
from movielog.viewings import api as viewings_api
from movielog.viewings import viewings_table


@pytest.fixture(autouse=True)
def init_db() -> None:
    viewings_table.reload([])


def test_create_serializes_new_viewing(tmp_path: str) -> None:
    expected = {
        "sequence": 1,
        "date": "2016-03-26",
        "imdb_id": "tt6019206",
        "title": "Kill Bill: The Whole Bloody Affair (2011)",
        "venue": "Alamo Drafthouse",
    }

    viewings_api.create(
        imdb_id="tt6019206",
        title="Kill Bill: The Whole Bloody Affair",
        year=2011,
        venue="Alamo Drafthouse",
        viewing_date=date(2016, 3, 26),
    )

    with open(
        os.path.join(tmp_path, "0001-kill-bill-the-whole-bloody-affair-2011.json"), "r"
    ) as output_file:
        file_content = json.load(output_file)

    assert file_content == expected


def test_create_raises_error_if_sequence_out_of_sync(tmp_path: str) -> None:
    existing_viewing = {
        "sequence": 3,
        "date": "2016-03-26",
        "imdb_id": "tt0266697",
        "title": "Kill Bill: Vol. 1 (2003)",
        "venue": "Alamo Drafthouse",
    }

    with open(
        os.path.join(tmp_path, "0003-kill-bill-vol-1-2003.json"), "w"
    ) as output_file:
        output_file.write(json.dumps(existing_viewing))

    with pytest.raises(SequenceError):
        viewings_api.create(
            imdb_id="tt6019206",
            title="Kill Bill: The Whole Bloody Affair",
            year=2011,
            venue="Alamo Drafthouse",
            viewing_date=date(2016, 3, 26),
        )


def test_venues_returns_sorted_venues(tmp_path: str) -> None:

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
        with open(
            os.path.join(tmp_path, "viewing-{0}.json".format(index)), "w"
        ) as output_file:
            output_file.write(json.dumps(existing_viewing))

    assert viewings_api.venues() == expected
