from __future__ import annotations

from movielog.reviews.exports import (  # noqa: WPS235
    grade_distributions,
    overrated_disappointments,
    review_stats,
    reviewed_movies,
    underseen_gems,
)


def export(watchlist_movie_ids: set[str]) -> None:  # noqa: WPS213
    grade_distributions.export()
    reviewed_movies.export()
    underseen_gems.export()
    overrated_disappointments.export()
    review_stats.export(watchlist_movie_ids=watchlist_movie_ids)
