from __future__ import annotations

from movielog.moviedata.core import (
    movies_table,
    names_dataset,
    title_akas_dataset,
    titles_dataset,
)


def refresh() -> None:
    titles_dataset.refresh()
    names_dataset.refresh()
    title_akas_dataset.refresh()


movie_ids = movies_table.movie_ids
