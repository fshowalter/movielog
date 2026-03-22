from __future__ import annotations

import json
from pathlib import Path

from movielog.cli import new_collection
from tests.cli.conftest import MockInput
from tests.cli.keys import Enter, Escape


def test_calls_add_collection(mock_input: MockInput, tmp_path: Path) -> None:
    mock_input(["Halloween", Enter, "y", "A horror movie franchise", Enter])
    new_collection.prompt()

    data = json.loads((tmp_path / "collections" / "halloween.json").read_text())
    assert data["name"] == "Halloween"
    assert data["slug"] == "halloween"
    assert data["description"] == "A horror movie franchise"
    assert data["titles"] == []


def test_does_not_call_add_viewing_if_no_movie(mock_input: MockInput, tmp_path: Path) -> None:
    mock_input([Escape])
    new_collection.prompt()

    assert not (tmp_path / "collections").exists()


def test_can_confirm_collection_name(mock_input: MockInput, tmp_path: Path) -> None:
    mock_input(["Halloween", Enter, "n"])
    new_collection.prompt()

    assert not (tmp_path / "collections").exists()
