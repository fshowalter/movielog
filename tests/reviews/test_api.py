import json
import os
from datetime import date

import pytest
from pytest_mock import MockerFixture

from movielog.reviews import api as reviews_api
from movielog.utils.sequence_tools import SequenceError


def test_most_recent_review_returns_most_recent_review() -> None:
    reviews_api.create(
        imdb_id="tt6019206",
        title="Kill Bill: The Whole Bloody Affair",
        year=2011,
        grade="B",
        venue="Alamo Drafthouse One Loudon",
        review_date=date(2016, 3, 12),
    )

    expected = reviews_api.create(
        imdb_id="tt6019206",
        title="Kill Bill: The Whole Bloody Affair",
        year=2011,
        grade="A",
        venue="Alamo Drafthouse One Loudon",
        review_date=date(2017, 3, 12),
    )

    expected.review_content = ""

    assert reviews_api.most_recent_review_for_movie("tt6019206") == expected


def test_most_recent_review_returns_none_if_no_reviews() -> None:

    assert reviews_api.most_recent_review_for_movie("tt6019206") is None


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


def test_movie_ids_returns_review_and_viewing_movie_ids(tmp_path: str) -> None:
    expected = set(
        ["tt0159693", "tt0025480", "tt0266697", "tt0053221", "tt0159693", "tt0031971"]
    )

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
            "date": "2006-04-29",
            "imdb_id": "tt0025480",
            "title": "Bad Seed (1934)",
            "venue": "Arte",
        },
        {
            "sequence": 3,
            "date": "2007-05-15",
            "imdb_id": "tt0266697",
            "title": "Kill Bill: Vol. 1 (2003)",
            "venue": "Alamo Drafthouse",
        },
        {
            "sequence": 4,
            "date": "2008-02-05",
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

    reviews_api.create(
        review_date=date(2010, 3, 12),
        imdb_id="tt0159693",
        title="Fright Night",
        year=1985,
        grade="A+",
        venue="AFI Silver",
    )
    reviews_api.create(
        review_date=date(2011, 7, 29),
        imdb_id="tt0031971",
        title="Stagecoach",
        year=1939,
        grade="A",
        venue="Blu-ray",
    )
    reviews_api.create(
        review_date=date(2020, 3, 12),
        imdb_id="tt0053221",
        title="Rio Bravo",
        year=1959,
        grade="A+",
        venue="Blu-ray",
    )

    assert expected == reviews_api.movie_ids()
