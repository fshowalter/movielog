from __future__ import annotations

from typing import TYPE_CHECKING

from movielog.moviedata.extended.tables import (
    countries_table,
    directing_credits_table,
    performing_credits_table,
    release_dates_table,
    sort_titles_table,
    writing_credits_table,
)

if TYPE_CHECKING:
    from movielog.moviedata.extended.movies import Movie


def reload(movies: list[Movie]) -> None:
    countries_table.update(movies)

    directing_credits_table.update(movies)

    performing_credits_table.update(movies)

    writing_credits_table.update(movies)

    release_dates_table.update(movies)

    sort_titles_table.update(movies)
