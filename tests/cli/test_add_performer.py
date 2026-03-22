from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from movielog.cli import add_performer
from movielog.repository.imdb_http_person import PersonPage
from tests.cli.conftest import MockInput
from tests.cli.keys import Down, Enter, Escape


@pytest.fixture(autouse=True)
def mock_search_person(monkeypatch: pytest.MonkeyPatch) -> None:
    mock = MagicMock(
        return_value=PersonPage(
            imdb_id="nm0000078",
            name="John Wayne",
            known_for_titles=["Rio Bravo", "The Searchers", "Stagecoach"],
        )
    )
    monkeypatch.setattr("movielog.cli.person_searcher.repository_api.get_person_page", mock)


def test_calls_add_performer(mock_input: MockInput, tmp_path: Path) -> None:
    mock_input(["a-test-aws-token", Enter, "nm0000078", Enter, Down, Enter, "y", Enter])
    add_performer.prompt()

    data = json.loads((tmp_path / "watchlist" / "performers" / "john-wayne.json").read_text())
    assert data["imdbId"] == "nm0000078"
    assert data["name"] == "John Wayne"
    assert data["slug"] == "john-wayne"


def test_can_confirm_selection(mock_input: MockInput, tmp_path: Path) -> None:
    mock_input(
        [
            "a-test-aws-token",
            Enter,
            "nm0000078",
            Enter,
            Down,
            Enter,
            "n",
            "nm0000078",
            Enter,
            Down,
            Enter,
            "y",
            Enter,
        ]
    )
    add_performer.prompt()

    data = json.loads((tmp_path / "watchlist" / "performers" / "john-wayne.json").read_text())
    assert data["imdbId"] == "nm0000078"


def test_does_not_call_add_performer_if_no_selection(mock_input: MockInput, tmp_path: Path) -> None:
    mock_input([Escape, Enter])
    add_performer.prompt()

    assert not (tmp_path / "watchlist" / "performers").exists()
