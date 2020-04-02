from typing import Callable

from movielog.watchlist_file import WatchlistFile


def test_replaces_unicode(build_watchlist_file: Callable[..., WatchlistFile]) -> None:
    watchlist_file = build_watchlist_file(name="Maléfique")
    assert watchlist_file.generate_slug() == "malefique"
