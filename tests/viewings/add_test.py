import json
import os
from datetime import date

import pytest
from pytest_mock import MockerFixture

from movielog import has_sequence, viewings


def test_creates_new_viewing(tmp_path: str, mocker: MockerFixture) -> None:
    mocker.patch("movielog.viewings.FOLDER_PATH", tmp_path)

    expected = {
        "sequence": 1,
        "date": "2016-03-26",
        "imdb_id": "tt6019206",
        "title": "Kill Bill: The Whole Bloody Affair (2011)",
        "venue": "Alamo Drafthouse",
    }

    viewings.add(
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


def test_raises_error_if_sequence_out_of_sync(
    tmp_path: str, mocker: MockerFixture
) -> None:
    mocker.patch("movielog.viewings.FOLDER_PATH", tmp_path)

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

    with pytest.raises(has_sequence.SequenceError):
        viewings.add(
            imdb_id="tt6019206",
            title="Kill Bill: The Whole Bloody Affair",
            year=2011,
            venue="Alamo Drafthouse",
            viewing_date=date(2016, 3, 26),
        )
