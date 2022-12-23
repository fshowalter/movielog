from __future__ import annotations

from movielog.viewings.exports import (  # noqa: WPS235
    most_watched_directors,
    most_watched_movies,
    most_watched_performers,
    most_watched_writers,
    top_media,
    viewing_counts_for_decades,
    viewing_stats,
    viewings,
)


def export() -> None:  # noqa: WPS213
    most_watched_directors.export()
    most_watched_movies.export()
    most_watched_performers.export()
    most_watched_writers.export()
    viewing_counts_for_decades.export()
    top_media.export()
    viewing_stats.export()
    viewings.export()
