from movielog.moviedata.core import (
    aka_titles_table,
    movies_table,
    names_dataset,
    people_table,
    title_akas_dataset,
    titles_dataset,
)


def refresh() -> None:
    titles_dataset.refresh(movies_table.reload)
    names_dataset.refresh(people_table.reload)
    title_akas_dataset.refresh(aka_titles_table.reload)


def movie_ids() -> set[str]:
    return movies_table.movie_ids()
