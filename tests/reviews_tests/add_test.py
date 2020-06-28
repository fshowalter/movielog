import os
from datetime import date

import pytest
from pytest_mock import MockFixture

from movielog import reviews, yaml_file


def test_creates_new_review(tmp_path: str, mocker: MockFixture) -> None:
    mocker.patch.object(reviews.Review, "folder_path", return_value=tmp_path)

    expected = "---\nsequence: 1\ndate: 2016-03-12\nimdb_id: tt6019206\ntitle: 'Kill Bill: The Whole Bloody Affair (2011)'\ngrade: A\nslug: kill-bill-the-whole-bloody-affair-2011\n---\n\n"  # noqa: 501

    reviews.add(
        imdb_id="tt6019206",
        title="Kill Bill: The Whole Bloody Affair",
        year=2011,
        grade="A",
        review_date=date(2016, 3, 12),
    )

    with open(
        os.path.join(tmp_path, "kill-bill-the-whole-bloody-affair-2011.md"), "r"
    ) as output_file:
        yaml_content = output_file.read()

    assert yaml_content == expected


def test_raises_error_if_sequence_out_of_sync(
    tmp_path: str, mocker: MockFixture
) -> None:
    mocker.patch.object(reviews.Review, "folder_path", return_value=tmp_path)

    existing_review = "---\nsequence: 3\ndate: 2016-03-12\nimdb_id: tt6019206\ntitle: 'Kill Bill: The Whole Bloody Affair (2011)'\ngrade: A\nslug: kill-bill-the-whole-bloody-affair-2011\n---\n\n"  # noqa: 501

    with open(
        os.path.join(tmp_path, "kill-bill-the-whole-bloody-affair-2011.md"), "w",
    ) as output_file:
        output_file.write(existing_review)

    with pytest.raises(yaml_file.YamlError):
        reviews.add(
            imdb_id="tt0266697",
            title="Kill Bill: Vol. 1",
            year=2003,
            grade="A",
            review_date=date(2026, 3, 12),
        )
