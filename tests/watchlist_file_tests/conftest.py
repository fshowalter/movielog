from typing import Callable, List, Optional

import pytest

from movielog.watchlist_file import Title, WatchlistFile


class ConcreteWatchlistFile(WatchlistFile):
    @classmethod
    def folder_path(cls) -> str:
        """Test stub."""


@pytest.fixture
def build_watchlist_file() -> Callable[..., WatchlistFile]:
    def _build_watchlist_file(
        name: str,
        imdb_id: Optional[str] = None,
        frozen: bool = False,
        titles: Optional[List[Title]] = None,
    ) -> WatchlistFile:
        return ConcreteWatchlistFile(
            name=name, imdb_id=imdb_id, frozen=frozen, titles=titles
        )

    return _build_watchlist_file
