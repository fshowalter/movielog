from __future__ import annotations

from pathlib import Path
from typing import Literal
from unittest.mock import MagicMock

import pytest

from movielog.cli import add_viewing
from movielog.cli.ask_medium_or_venue import ReturnResult as MediumOrVenueReturnResult
from movielog.repository.imdb_http_title import TitlePage
from tests.cli.conftest import MockInput
from tests.cli.keys import Backspace, End, Enter, Escape
from tests.cli.prompt_utils import ConfirmType, enter_text, select_option


@pytest.fixture(autouse=True)
def mock_search_title(monkeypatch: pytest.MonkeyPatch) -> None:
    mock = MagicMock(
        return_value=TitlePage(
            imdb_id="tt0053221",
            title="Rio Bravo",
            year=1959,
            principal_cast=["John Wayne", "Dean Martin", "Ricky Nelson"],
            genres=["Western"],
            release_date="1959-03-08",
            release_date_country="USA",
            original_title="Rio Bravo",
            countries=["USA"],
            runtime_minutes=141,
            credits={},
        )
    )
    monkeypatch.setattr("movielog.cli.title_searcher.repository_api.get_title_page", mock)


def enter_token() -> list[str]:
    return enter_text("a-test-aws-token")


def enter_title(title: str) -> list[str]:
    return enter_text(title)


def select_title_search_result(confirm: ConfirmType) -> list[str]:
    return select_option(1, confirm=confirm)


def select_if_medium_or_venue(medium_or_venue: MediumOrVenueReturnResult) -> list[str]:
    return [medium_or_venue]


def select_medium() -> list[str]:
    return select_option(2)


def select_venue() -> list[str]:
    return select_option(1)


def enter_medium_notes(notes: str) -> list[str]:
    return enter_text(notes)


def enter_grade(grade: str) -> list[str]:
    return enter_text(grade)


def add_another_viewing(confirm: ConfirmType) -> list[str]:
    return [confirm]


def enter_if_review(confirm: ConfirmType) -> list[str]:
    return [confirm]


def enter_viewing_date(date: str, confirm: Literal[ConfirmType] | None = None) -> list[str]:
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


def test_calls_add_viewing_and_create_or_update_review(
    mock_input: MockInput,
    tmp_path: Path,
) -> None:
    mock_input(
        [
            *enter_token(),
            *enter_title("tt0053221"),
            *select_title_search_result("y"),
            *enter_viewing_date("2012-03-12", confirm="y"),
            *select_if_medium_or_venue("m"),
            *select_medium(),
            *enter_medium_notes("Warner Bros., 2012"),
            *enter_if_review("y"),
            *enter_grade("A+"),
            *add_another_viewing("n"),
        ]
    )

    add_viewing.prompt()

    viewing_file = tmp_path / "viewings" / "2012-03-12-01-rio-bravo-1959.md"
    assert viewing_file.exists()
    viewing_content = viewing_file.read_text()
    assert "imdbId: tt0053221" in viewing_content
    assert "medium: TCM HD" in viewing_content
    assert "mediumNotes: Warner Bros., 2012" in viewing_content
    assert "venue: null" in viewing_content

    review_file = tmp_path / "rio-bravo-1959.md"
    assert review_file.exists()
    review_content = review_file.read_text()
    assert "imdb_id: tt0053221" in review_content
    assert "grade: A+" in review_content
    assert "date: 2012-03-12" in review_content


def test_can_confirm_title(
    mock_input: MockInput,
    tmp_path: Path,
) -> None:
    mock_input(
        [
            *enter_token(),
            *enter_title("tt0051554"),
            *select_title_search_result("n"),
            *enter_title("tt0053221"),
            *select_title_search_result("y"),
            *enter_viewing_date("2012-03-12", confirm="y"),
            *select_if_medium_or_venue("m"),
            *select_medium(),
            *enter_medium_notes("Warner Bros., 2017"),
            *enter_if_review("y"),
            *enter_grade("A+"),
            *add_another_viewing("n"),
        ]
    )
    add_viewing.prompt()

    viewing_file = tmp_path / "viewings" / "2012-03-12-01-rio-bravo-1959.md"
    assert viewing_file.exists()
    assert "mediumNotes: Warner Bros., 2017" in viewing_file.read_text()


def test_does_not_call_add_viewing_or_create_or_update_review_if_no_title(
    mock_input: MockInput,
    tmp_path: Path,
) -> None:
    mock_input([Escape])
    add_viewing.prompt()

    assert not (tmp_path / "viewings" / "2012-03-12-01-rio-bravo-1959.md").exists()
    assert not (tmp_path / "rio-bravo-1959.md").exists()


def test_does_not_call_add_viewing_or_create_or_update_review_if_no_date(
    mock_input: MockInput,
    tmp_path: Path,
) -> None:
    mock_input(
        [
            *enter_token(),
            *enter_title("tt0053221"),
            *select_title_search_result("y"),
            Escape,
            Escape,
            Escape,
        ]
    )
    add_viewing.prompt()

    assert not (tmp_path / "viewings" / "2012-03-12-01-rio-bravo-1959.md").exists()
    assert not (tmp_path / "rio-bravo-1959.md").exists()


def test_guards_against_bad_dates(
    mock_input: MockInput,
    tmp_path: Path,
) -> None:
    mock_input(
        [
            *enter_token(),
            *enter_title("tt0053221"),
            *select_title_search_result("y"),
            *enter_viewing_date("2012-03-32"),
            *enter_viewing_date("2012-03-12", confirm="y"),
            *select_if_medium_or_venue("m"),
            *select_medium(),
            *enter_medium_notes("Warner Bros., 2012"),
            *enter_if_review("y"),
            *enter_grade("A+"),
            *add_another_viewing("n"),
        ]
    )
    add_viewing.prompt()

    viewing_file = tmp_path / "viewings" / "2012-03-12-01-rio-bravo-1959.md"
    assert viewing_file.exists()
    assert "imdbId: tt0053221" in viewing_file.read_text()


def test_can_confirm_date(
    mock_input: MockInput,
    tmp_path: Path,
) -> None:
    mock_input(
        [
            *enter_token(),
            *enter_title("tt0053221"),
            *select_title_search_result("y"),
            *enter_viewing_date("2012-03-13", confirm="n"),
            *enter_viewing_date("2012-03-12", confirm="y"),
            *select_if_medium_or_venue("m"),
            *select_medium(),
            *enter_medium_notes("Warner Bros., 2012"),
            *enter_if_review("y"),
            *enter_grade("A+"),
            *add_another_viewing("n"),
        ]
    )
    add_viewing.prompt()

    viewing_file = tmp_path / "viewings" / "2012-03-12-01-rio-bravo-1959.md"
    assert viewing_file.exists()
    assert "imdbId: tt0053221" in viewing_file.read_text()


def test_can_add_new_medium(mock_input: MockInput, tmp_path: Path) -> None:
    mock_input(
        [
            *enter_token(),
            *enter_title("tt0053221"),
            *select_title_search_result("y"),
            *enter_viewing_date("2012-03-12", confirm="y"),
            *select_if_medium_or_venue("m"),
            End,
            Enter,
            *enter_text("4k UHD Blu-ray"),
            *enter_medium_notes("Warner Bros., 2023"),
            *enter_if_review("y"),
            *enter_grade("A+"),
            *add_another_viewing("n"),
        ]
    )
    add_viewing.prompt()

    viewing_file = tmp_path / "viewings" / "2012-03-12-01-rio-bravo-1959.md"
    assert viewing_file.exists()
    viewing_content = viewing_file.read_text()
    assert "medium: 4k UHD Blu-ray" in viewing_content
    assert "mediumNotes: Warner Bros., 2023" in viewing_content


def test_can_create_with_venue(mock_input: MockInput, tmp_path: Path) -> None:
    mock_input(
        [
            *enter_token(),
            *enter_title("tt0053221"),
            *select_title_search_result("y"),
            *enter_viewing_date("2012-03-12", confirm="y"),
            *select_if_medium_or_venue("v"),
            *select_venue(),
            *enter_if_review("y"),
            *enter_grade("A+"),
            *add_another_viewing("n"),
        ]
    )
    add_viewing.prompt()

    viewing_file = tmp_path / "viewings" / "2012-03-12-01-rio-bravo-1959.md"
    assert viewing_file.exists()
    viewing_content = viewing_file.read_text()
    assert "venue: AMC Tysons Corner 16" in viewing_content
    assert "medium: null" in viewing_content


def test_can_add_new_venue(mock_input: MockInput, tmp_path: Path) -> None:
    mock_input(
        [
            *enter_token(),
            *enter_title("tt0053221"),
            *select_title_search_result("y"),
            *enter_viewing_date("2012-03-12", confirm="y"),
            *select_if_medium_or_venue("v"),
            End,
            Enter,
            *enter_text("Alamo Drafthouse"),
            *enter_if_review("y"),
            *enter_grade("A+"),
            *add_another_viewing("n"),
        ]
    )
    add_viewing.prompt()

    viewing_file = tmp_path / "viewings" / "2012-03-12-01-rio-bravo-1959.md"
    assert viewing_file.exists()
    assert "venue: Alamo Drafthouse" in viewing_file.read_text()


def test_does_not_call_add_viewing_or_create_or_update_review_if_no_medium(
    mock_input: MockInput,
    tmp_path: Path,
) -> None:
    mock_input(
        [
            *enter_token(),
            *enter_title("tt0053221"),
            *select_title_search_result("y"),
            *enter_viewing_date("2012-03-12", confirm="y"),
            Escape,
            Escape,
            Escape,
            Escape,
            Escape,
            Escape,
        ]
    )
    add_viewing.prompt()

    assert not (tmp_path / "viewings" / "2012-03-12-01-rio-bravo-1959.md").exists()
    assert not (tmp_path / "rio-bravo-1959.md").exists()
