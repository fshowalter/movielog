import os
from datetime import date

import pytest
from pytest_mock import MockerFixture

from movielog.reviews import api as reviews_api
from movielog.utils.sequence_tools import SequenceError


def test_create_serializes_new_review(tmp_path: str) -> None:
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


def test_create_raises_error_if_sequence_out_of_sync(tmp_path: str) -> None:
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


def test_export_data_updates_reviews_and_viewings_table(mocker: MockerFixture) -> None:
    viewings_table_update_mock = mocker.patch(
        "movielog.reviews.api.viewings_table.update"
    )
    reviews_table_update_mock = mocker.patch(
        "movielog.reviews.api.reviews_table.update"
    )
    mocker.patch("movielog.reviews.api.exports_api")

    reviews_api.export_data()

    viewings_table_update_mock.assert_called_once()
    reviews_table_update_mock.assert_called_once()
