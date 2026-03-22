from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from movielog.cli import add_director
from movielog.repository.imdb_http_person import PersonPage
from tests.cli.conftest import MockInput
from tests.cli.keys import Down, Enter, Escape


@pytest.fixture(autouse=True)
def mock_search_person(monkeypatch: pytest.MonkeyPatch) -> None:
    mock = MagicMock(
        return_value=PersonPage(
            imdb_id="nm0001328",
            name="Howard Hawks",
            known_for_titles=["Scarface", "Rio Bravo", "Only Angels Have Wings"],
        )
    )
    monkeypatch.setattr("movielog.cli.person_searcher.repository_api.get_person_page", mock)


def test_calls_add_director(mock_input: MockInput, tmp_path: Path) -> None:
    mock_input(["a-test-aws-token", Enter, "nm0001328", Enter, Down, Enter, "y", Enter])
    add_director.prompt()

    data = json.loads((tmp_path / "watchlist" / "directors" / "howard-hawks.json").read_text())
    assert data["imdbId"] == "nm0001328"
    assert data["name"] == "Howard Hawks"
    assert data["slug"] == "howard-hawks"


def test_does_not_call_add_director_if_no_selection(mock_input: MockInput, tmp_path: Path) -> None:
    mock_input([Escape, Enter])
    add_director.prompt()

    assert not (tmp_path / "watchlist" / "directors" / "howard-hawks.json").exists()
