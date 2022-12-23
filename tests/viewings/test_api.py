import json
import os
from datetime import date

import pytest
from pytest_mock import MockerFixture

from movielog.utils.sequence_tools import SequenceError
from movielog.viewings import api as viewings_api


def test_last_viewing_date_returns_last_viewing_date() -> None:
    viewings_api.create(
        imdb_id="tt6019206",
        slug="kill-bill-vol-1-2003",
        viewing_date=date(2016, 3, 12),
        medium="Blu-ray",
    )

    viewings_api.create(
        imdb_id="tt6019206",
        slug="kill-bill-vol-1-2003",
        viewing_date=date(2017, 3, 12),
        medium="Blu-ray",
    )

    expected = date(2017, 3, 12)

    assert viewings_api.last_viewing_date() == expected


def test_last_viewing_date_returns_none_if_no_viewings() -> None:

    assert viewings_api.last_viewing_date() is None


def test_create_serializes_new_viewing(tmp_path: str) -> None:
    expected = json.dumps(
        {
            "sequence": 1,
            "date": "2016-03-12",
            "imdb_id": "tt6019206",
            "slug": "kill-bill-the-whole-bloody-affair-2011",
            "medium": "Blu-ray",
            "medium_notes": None,
            "venue": None,
        },
        indent=4,
    )

    viewings_api.create(
        imdb_id="tt6019206",
        slug="kill-bill-the-whole-bloody-affair-2011",
        medium="Blu-ray",
        viewing_date=date(2016, 3, 12),
    )

    with open(
        os.path.join(tmp_path, "0001-kill-bill-the-whole-bloody-affair-2011.json"), "r"
    ) as output_file:
        file_content = output_file.read()

    assert file_content == expected


def test_create_raises_error_if_sequence_out_of_sync(tmp_path: str) -> None:
    existing_viewing = json.dumps(
        {
            "sequence": 3,
            "date": "2016-03-12",
            "imdb_id": "tt6019206",
            "slug": "kill-bill-the-whole-bloody-affair-2011",
            "medium": "Blu-ray",
            "medium_notes": None,
            "venue": None,
        }
    )

    with open(
        os.path.join(tmp_path, "0003-kill-bill-the-whole-bloody-affair-2011.json"),
        "w",
    ) as output_file:
        output_file.write(existing_viewing)

    with pytest.raises(SequenceError):
        viewings_api.create(
            imdb_id="tt0266697",
            medium="Blu-ray",
            slug="kill-bill-vol-1-2003",
            viewing_date=date(2026, 3, 12),
        )


def test_export_data_updates_viewings_table(mocker: MockerFixture) -> None:
    viewings_table_update_mock = mocker.patch(
        "movielog.viewings.api.viewings_table.update"
    )

    mocker.patch("movielog.viewings.api.exports_api")

    viewings_api.export_data()

    viewings_table_update_mock.assert_called_once()


def test_movie_ids_returns_viewing_movie_ids(tmp_path: str) -> None:
    expected = set(
        [
            "tt0159693",
            "tt0025480",
            "tt0266697",
            "tt0053221",
        ]
    )

    existing_viewings = [
        {
            "sequence": 1,
            "date": "2005-03-26",
            "imdb_id": "tt0159693",
            "slug": "razor-blade-smile-1998",
            "medium": "DVD",
            "medium_notes": None,
            "venue": None,
        },
        {
            "sequence": 2,
            "date": "2006-04-29",
            "imdb_id": "tt0025480",
            "slug": "bad-seed-1934",
            "medium": "Arte",
            "medium_notes": None,
            "venue": None,
        },
        {
            "sequence": 3,
            "date": "2007-05-15",
            "imdb_id": "tt0266697",
            "slug": "kill-bill-vol-1-2003",
            "medium": "Alamo Drafthouse",
            "medium_notes": None,
            "venue": None,
        },
        {
            "sequence": 4,
            "date": "2008-02-05",
            "imdb_id": "tt0053221",
            "slug": "rio-bravo-1959",
            "medium": "Blu-ray",
            "medium_notes": None,
            "venue": None,
        },
    ]

    for index, existing_viewing in enumerate(existing_viewings):
        with open(
            os.path.join(tmp_path, "viewing-{0}.json".format(index)), "w"
        ) as output_file:
            output_file.write(json.dumps(existing_viewing))

    assert expected == viewings_api.movie_ids()
