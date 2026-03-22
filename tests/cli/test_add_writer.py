from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from movielog.cli import add_writer
from movielog.repository.imdb_http_person import PersonPage
from tests.cli.conftest import MockInput
from tests.cli.keys import Down, Enter, Escape


@pytest.fixture(autouse=True)
def mock_search_person(monkeypatch: pytest.MonkeyPatch) -> None:
    mock = MagicMock(
        return_value=PersonPage(
            imdb_id="nm0102824",
            name="Leigh Brackett",
            known_for_titles=["Rio Bravo", "The Big Sleep", "The Empire Strikes Back"],
        )
    )
    monkeypatch.setattr("movielog.cli.person_searcher.repository_api.get_person_page", mock)


def test_calls_add_writer(mock_input: MockInput, tmp_path: Path) -> None:
    mock_input(["a-test-aws-token", Enter, "nm0102824", Enter, Down, Enter, "y", Enter])
    add_writer.prompt()

    data = json.loads((tmp_path / "watchlist" / "writers" / "leigh-brackett.json").read_text())
    assert data["imdbId"] == "nm0102824"
    assert data["name"] == "Leigh Brackett"
    assert data["slug"] == "leigh-brackett"


def test_does_not_call_add_writer_if_no_selection(mock_input: MockInput, tmp_path: Path) -> None:
    mock_input([Escape, Enter])
    add_writer.prompt()

    assert not (tmp_path / "watchlist" / "writers").exists()
