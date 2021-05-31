import os
from datetime import date

import pytest
from pytest_mock import MockerFixture

from movielog.reviews import api as reviews_api
from movielog.reviews import reviews_table
from movielog.utils.sequence_tools import SequenceError


@pytest.fixture(autouse=True)
def init_db() -> None:
    reviews_table.reload([])


def test_create_serializes_new_review(tmp_path: str, mocker: MockerFixture) -> None:
    expected = "---\nsequence: 1\ndate: 2016-03-12\nimdb_id: tt6019206\ntitle: 'Kill Bill: The Whole Bloody Affair (2011)'\ngrade: A\nslug: kill-bill-the-whole-bloody-affair-2011\nvenue: Alamo Drafthouse One Loudon\nvenue_notes:\n---\n\n"  # noqa: 501

    reviews_api.create(
        imdb_id="tt6019206",
        title="Kill Bill: The Whole Bloody Affair",
        year=2011,
        grade="A",
        venue="Alamo Drafthouse One Loudon",
        review_date=date(2016, 3, 12),
    )

    with open(
        os.path.join(tmp_path, "0001-kill-bill-the-whole-bloody-affair-2011.md"), "r"
    ) as output_file:
        file_content = output_file.read()

    assert file_content == expected


def test_create_raises_error_if_sequence_out_of_sync(
    tmp_path: str, mocker: MockerFixture
) -> None:
    existing_review = "---\nsequence: 3\ndate: 2016-03-12\nimdb_id: tt6019206\ntitle: 'Kill Bill: The Whole Bloody Affair (2011)'\ngrade: A\nslug: kill-bill-the-whole-bloody-affair-2011\nvenue: Alamo Drafthouse One Loudon\nvenue_notes:\n---\n\n"  # noqa: 501

    with open(
        os.path.join(tmp_path, "0003-kill-bill-the-whole-bloody-affair-2011.md"),
        "w",
    ) as output_file:
        output_file.write(existing_review)

    with pytest.raises(SequenceError):
        reviews_api.create(
            imdb_id="tt0266697",
            title="Kill Bill: Vol. 1",
            year=2003,
            grade="A",
            venue="Alamo Drafthouse One Loudon",
            review_date=date(2026, 3, 12),
        )
