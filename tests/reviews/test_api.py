import os
from datetime import date

from pytest_mock import MockerFixture

from movielog.reviews import api as reviews_api


def test_most_recent_review_returns_most_recent_review() -> None:
    reviews_api.create_or_update(
        imdb_id="tt6019206",
        grade="B",
        slug="kill-bill-vol-1-2003",
        review_date=date(2016, 3, 12),
    )

    expected = reviews_api.create_or_update(
        imdb_id="tt6019206",
        slug="kill-bill-vol-1-2003",
        grade="A",
        review_date=date(2017, 3, 12),
    )

    expected.review_content = ""

    assert reviews_api.review_for_movie("tt6019206") == expected


def test_most_recent_review_returns_none_if_no_reviews() -> None:

    assert reviews_api.review_for_movie("tt6019206") is None


def test_create_serializes_new_review(tmp_path: str) -> None:
    expected = "---\ndate: 2016-03-12\nimdb_id: tt6019206\ngrade: A\nslug: kill-bill-the-whole-bloody-affair-2011\n---\n\n"  # noqa: 501

    reviews_api.create_or_update(
        imdb_id="tt6019206",
        slug="kill-bill-the-whole-bloody-affair-2011",
        grade="A",
        review_date=date(2016, 3, 12),
    )

    with open(
        os.path.join(tmp_path, "kill-bill-the-whole-bloody-affair-2011.md"), "r"
    ) as output_file:
        file_content = output_file.read()

    assert file_content == expected


def test_export_data_updates_reviews_table(mocker: MockerFixture) -> None:
    reviews_table_update_mock = mocker.patch(
        "movielog.reviews.api.reviews_table.update"
    )
    mocker.patch("movielog.reviews.api.exports_api")

    reviews_api.export_data()

    reviews_table_update_mock.assert_called_once()
