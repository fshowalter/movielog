from typing import Any, Callable, Dict

import pytest

from movielog.watchlist_file import WatchlistFile


class ConcreteWatchlistFile(WatchlistFile):
    @classmethod
    def from_yaml_object(cls, yaml_object: Dict[str, Any]) -> "ConcreteWatchlistFile":
        """Test stub."""

    @classmethod
    def folder_path(cls) -> str:
        """Test stub."""


@pytest.fixture
def build_watchlist_file() -> Callable[[str], WatchlistFile]:
    def _build_watchlist_file(name: str) -> WatchlistFile:
        return ConcreteWatchlistFile(name=name)

    return _build_watchlist_file
