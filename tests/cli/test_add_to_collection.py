from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from movielog.cli import add_to_collection
from movielog.repository.imdb_http_title import TitlePage
from tests.cli.conftest import MockInput
from tests.cli.keys import Escape
from tests.cli.prompt_utils import ConfirmType, enter_text, select_option


def enter_token() -> list[str]:
    return enter_text("a-test-aws-token")


def enter_title(title: str) -> list[str]:
    return enter_text(title)


def select_collection() -> list[str]:
    return select_option(1)


def select_title_search_result(confirm: ConfirmType) -> list[str]:
    return select_option(1, confirm=confirm)


@pytest.fixture(autouse=True)
def mock_search_title(monkeypatch: pytest.MonkeyPatch) -> None:
    mock = MagicMock(
        return_value=TitlePage(
            imdb_id="tt0087298",
            title="Friday the 13th: The Final Chapter",
            year=1984,
            principal_cast=["Erich Anderson", "Judie Aronson", "Peter Barton"],
            genres=["Horror", "Thriller"],
            release_date="1984-04-13",
            release_date_country="USA",
            original_title="Friday the 13th: The Final Chapter",
            countries=["USA"],
            runtime_minutes=91,
            credits={},
        )
    )
    monkeypatch.setattr("movielog.cli.title_searcher.repository_api.get_title_page", mock)


@pytest.fixture(autouse=True)
def seed_collection(tmp_path: Path) -> None:
    collections_dir = tmp_path / "collections"
    collections_dir.mkdir(parents=True, exist_ok=True)
    (collections_dir / "friday-the-13th.json").write_text(
        json.dumps(
            {
                "name": "Friday the 13th",
                "slug": "friday-the-13th",
                "titles": [
                    {"imdbId": "tt0080761", "title": "Friday the 13th (1980)"},
                    {"imdbId": "tt0082418", "title": "Friday the 13th Part 2 (1981)"},
                    {"imdbId": "tt0083972", "title": "Friday the 13th Part III (1982)"},
                ],
                "description": "The Friday the 13th franchise.",
            }
        )
    )


def test_calls_add_title_to_collection(mock_input: MockInput, tmp_path: Path) -> None:
    mock_input(
        [
            *select_collection(),
            *enter_token(),
            *enter_title("tt0087298"),
            *select_title_search_result(confirm="y"),
            Escape,
            Escape,
        ]
    )
    add_to_collection.prompt()

    data = json.loads((tmp_path / "collections" / "friday-the-13th.json").read_text())
    assert len(data["titles"]) == 4
    assert {"imdbId": "tt0087298", "title": "Friday the 13th: The Final Chapter (1984)"} in data[
        "titles"
    ]


def test_does_not_call_add_title_to_collection_if_no_selection(
    mock_input: MockInput,
    tmp_path: Path,
) -> None:
    mock_input(
        [
            *select_collection(),
            *enter_token(),
            *enter_title("The Final Chapter"),
            Escape,
            Escape,
            Escape,
            Escape,
        ]
    )
    add_to_collection.prompt()

    data = json.loads((tmp_path / "collections" / "friday-the-13th.json").read_text())
    assert len(data["titles"]) == 3
