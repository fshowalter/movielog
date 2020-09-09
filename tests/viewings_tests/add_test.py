import os
from datetime import date

import pytest
from pytest_mock import MockerFixture

from movielog import viewings, yaml_file


def test_creates_new_viewing(tmp_path: str, mocker: MockerFixture) -> None:
    mocker.patch("movielog.viewings.TABLE_NAME", tmp_path)

    expected = "sequence: 1\ndate: 2016-03-26\nimdb_id: tt6019206\ntitle: 'Kill Bill: The Whole Bloody Affair (2011)'\nvenue: Alamo Drafthouse\n"  # noqa: 501

    viewings.add(
        imdb_id="tt6019206",
        title="Kill Bill: The Whole Bloody Affair",
        year=2011,
        venue="Alamo Drafthouse",
        viewing_date=date(2016, 3, 26),
    )

    with open(
        os.path.join(tmp_path, "0001-kill-bill-the-whole-bloody-affair-2011.yml"), "r"
    ) as output_file:
        yaml_content = output_file.read()

    assert yaml_content == expected


def test_raises_error_if_sequence_out_of_sync(
    tmp_path: str, mocker: MockerFixture
) -> None:
    mocker.patch("movielog.viewings.TABLE_NAME", tmp_path)

    existing_viewing = "sequence: 3\ndate: 2006-03-26\nimdb_id: tt0266697\ntitle: 'Kill Bill: Vol. 1 (2003)'\nvenue: Alamo Drafthouse\n"  # noqa: 501

    with open(
        os.path.join(tmp_path, "0001-kill-bill-the-whole-bloody-affair-2011.yml"), "w"
    ) as output_file:
        output_file.write(existing_viewing)

    with pytest.raises(yaml_file.YamlError):
        viewings.add(
            imdb_id="tt6019206",
            title="Kill Bill: The Whole Bloody Affair",
            year=2011,
            venue="Alamo Drafthouse",
            viewing_date=date(2016, 3, 26),
        )
