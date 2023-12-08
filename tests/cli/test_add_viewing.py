from datetime import date
from typing import Literal, Optional
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture

from movielog.cli import add_viewing
from movielog.repository.datasets.dataset_title import DatasetTitle
from movielog.repository.db import titles_table
from tests.cli.conftest import MockInput
from tests.cli.keys import Backspace, End, Enter, Escape
from tests.cli.prompt_utils import ConfirmType, enter_text, select_option


@pytest.fixture(autouse=True)
def mock_add_viewing(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.add_viewing.repository_api.create_viewing")


@pytest.fixture(autouse=True)
def mock_create_or_update_review(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "movielog.cli.add_viewing.repository_api.create_or_update_review"
    )


@pytest.fixture(autouse=True)
def seed_db() -> None:
    titles_table.reload(
        [
            DatasetTitle(
                imdb_id="tt0051554",
                title="Horror of Dracula",
                full_title="Horror of Dracula (1958)",
                aka_titles=[],
                original_title="Dracula",
                year="1958",
                runtime_minutes=97,
                principal_cast=["Peter Cushing", "Christopher Lee"],
                imdb_votes=23,
                imdb_rating=4.5,
            ),
            DatasetTitle(
                imdb_id="tt0053221",
                title="Rio Bravo",
                full_title="Rio Bravo (1959)",
                original_title="Rio Bravo",
                aka_titles=["Howard Hawks' Rio Bravo"],
                year="1959",
                runtime_minutes=121,
                principal_cast=["John Wayne", "Dean Martin", "Ricky Nelson"],
                imdb_votes=32,
                imdb_rating=7.8,
            ),
            DatasetTitle(
                imdb_id="tt0050280",
                title="Curse of Frankenstein",
                full_title="Curse of Frankenstein (1957)",
                aka_titles=[],
                original_title="Curse of Frankenstein",
                year="1957",
                runtime_minutes=98,
                principal_cast=["Peter Cushing", "Christopher Lee"],
                imdb_votes=16,
                imdb_rating=5.8,
            ),
        ]
    )


def enter_title(title: str) -> list[str]:
    return enter_text(title)


def select_title_search_result(confirm: ConfirmType) -> list[str]:
    return select_option(1, confirm=confirm)


def select_medium() -> list[str]:
    return select_option(2)


def enter_grade(grade: str) -> list[str]:
    return enter_text(grade)


def add_another_viewing(confirm: ConfirmType) -> list[str]:
    return [confirm]


def enter_viewing_date(
    date: str, confirm: Optional[Literal[ConfirmType]] = None
) -> list[str]:
    input_stream = [
        Backspace,
        Backspace,
        Backspace,
        Backspace,
        Backspace,
        Backspace,
        Backspace,
        Backspace,
        Backspace,
        Backspace,
        *enter_text(date),
    ]

    if confirm:
        input_stream.append(confirm)

    return input_stream


@freeze_time("2012-12-01")
def test_calls_add_viewing_and_create_or_update_review(
    mock_input: MockInput,
    mock_add_viewing: MagicMock,
    mock_create_or_update_review: MagicMock,
) -> None:
    mock_input(
        [
            *enter_title("Rio Bravo"),
            *select_title_search_result("y"),
            *enter_viewing_date("2012-03-12", confirm="y"),
            *select_medium(),
            *enter_grade("A+"),
            *add_another_viewing("n"),
        ]
    )

    add_viewing.prompt()

    mock_add_viewing.assert_called_once_with(
        imdb_id="tt0053221",
        full_title="Rio Bravo (1959)",
        medium="TCM HD",
        date=date(2012, 3, 12),
    )

    mock_create_or_update_review.assert_called_once_with(
        imdb_id="tt0053221",
        full_title="Rio Bravo (1959)",
        grade="A+",
        date=date(2012, 3, 12),
    )


@freeze_time("2012-12-01")
def test_can_confirm_title(
    mock_input: MockInput,
    mock_add_viewing: MagicMock,
    mock_create_or_update_review: MagicMock,
) -> None:
    mock_input(
        [
            *enter_title("Horror of Dracula"),
            *select_title_search_result("n"),
            *enter_title("Rio Bravo"),
            *select_title_search_result("y"),
            *enter_viewing_date("2012-03-12", confirm="y"),
            *select_medium(),
            *enter_grade("A+"),
            *add_another_viewing("n"),
        ]
    )
    add_viewing.prompt()

    mock_add_viewing.assert_called_once_with(
        imdb_id="tt0053221",
        full_title="Rio Bravo (1959)",
        medium="TCM HD",
        date=date(2012, 3, 12),
    )

    mock_create_or_update_review.assert_called_once_with(
        imdb_id="tt0053221",
        full_title="Rio Bravo (1959)",
        grade="A+",
        date=date(2012, 3, 12),
    )


def test_does_not_call_add_viewing_or_create_or_update_review_if_no_title(
    mock_input: MockInput,
    mock_add_viewing: MagicMock,
    mock_create_or_update_review: MagicMock,
) -> None:
    mock_input([Escape])
    add_viewing.prompt()

    mock_add_viewing.assert_not_called()
    mock_create_or_update_review.assert_not_called()


def test_does_not_call_add_viewing_or_create_or_update_review_if_no_date(
    mock_input: MockInput,
    mock_add_viewing: MagicMock,
    mock_create_or_update_review: MagicMock,
) -> None:
    mock_input(
        [
            *enter_title("Rio Bravo"),
            *select_title_search_result("y"),
            Escape,
            Escape,
            Escape,
        ]
    )
    add_viewing.prompt()

    mock_add_viewing.assert_not_called()
    mock_create_or_update_review.assert_not_called()


@freeze_time("2012-12-01")
def test_guards_against_bad_dates(
    mock_input: MockInput,
    mock_add_viewing: MagicMock,
    mock_create_or_update_review: MagicMock,
) -> None:
    mock_input(
        [
            *enter_title("Rio Bravo"),
            *select_title_search_result("y"),
            *enter_viewing_date("2012-03-32"),
            *enter_viewing_date("2012-03-12", confirm="y"),
            *select_medium(),
            *enter_grade("A+"),
            *add_another_viewing("n"),
        ]
    )
    add_viewing.prompt()

    mock_add_viewing.assert_called_once_with(
        imdb_id="tt0053221",
        full_title="Rio Bravo (1959)",
        medium="TCM HD",
        date=date(2012, 3, 12),
    )

    mock_create_or_update_review.assert_called_once_with(
        imdb_id="tt0053221",
        full_title="Rio Bravo (1959)",
        grade="A+",
        date=date(2012, 3, 12),
    )


@freeze_time("2012-12-01")
def test_can_confirm_date(
    mock_input: MockInput,
    mock_add_viewing: MagicMock,
    mock_create_or_update_review: MagicMock,
) -> None:
    mock_input(
        [
            *enter_title("Rio Bravo"),
            *select_title_search_result("y"),
            *enter_viewing_date("2012-03-13", confirm="n"),
            *enter_viewing_date("2012-03-12", confirm="y"),
            *select_medium(),
            *enter_grade("A+"),
            *add_another_viewing("n"),
        ]
    )
    add_viewing.prompt()

    mock_add_viewing.assert_called_once_with(
        imdb_id="tt0053221",
        full_title="Rio Bravo (1959)",
        medium="TCM HD",
        date=date(2012, 3, 12),
    )

    mock_create_or_update_review.assert_called_once_with(
        imdb_id="tt0053221",
        full_title="Rio Bravo (1959)",
        grade="A+",
        date=date(2012, 3, 12),
    )


@freeze_time("2012-12-01")
def test_can_add_new_medium(mock_input: MockInput, mock_add_viewing: MagicMock) -> None:
    mock_input(
        [
            *enter_title("Rio Bravo"),
            *select_title_search_result("y"),
            *enter_viewing_date("2012-03-12", confirm="y"),
            End,
            Enter,
            *enter_text("4k UHD Blu-ray"),
            *enter_grade("A+"),
            *add_another_viewing("n"),
        ]
    )
    add_viewing.prompt()

    mock_add_viewing.assert_called_once_with(
        imdb_id="tt0053221",
        full_title="Rio Bravo (1959)",
        medium="4k UHD Blu-ray",
        date=date(2012, 3, 12),
    )


@freeze_time("2012-12-01")
def test_does_not_call_add_viewing_or_create_or_update_review_if_no_medium(
    mock_input: MockInput,
    mock_add_viewing: MagicMock,
    mock_create_or_update_review: MagicMock,
) -> None:
    mock_input(
        [
            *enter_title("Rio Bravo"),
            *select_title_search_result("y"),
            *enter_viewing_date("2012-03-12", confirm="y"),
            Escape,
            Escape,
            Escape,
            Escape,
            Escape,
        ]
    )
    add_viewing.prompt()

    mock_add_viewing.assert_not_called()
    mock_create_or_update_review.assert_not_called()
