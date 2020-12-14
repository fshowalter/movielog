from typing import Sequence, Set

from movielog import (
    imdb_data,
    most_watched_movies,
    most_watched_people,
    reviews,
    viewings,
    watchlist,
    watchlist_exporter,
)

Viewing = viewings.Viewing


def existing_imdb_ids(
    viewings_movies: Sequence[Viewing], watchlist_movies: Sequence[watchlist.Movie]
) -> Set[str]:
    viewing_imdb_ids = set([viewing_movie.imdb_id for viewing_movie in viewings_movies])
    watchlist_imdb_ids = set(
        [watchlist_movie.movie_imdb_id for watchlist_movie in watchlist_movies]
    )
    return viewing_imdb_ids.union(watchlist_imdb_ids)


def export() -> None:
    viewings_movies = viewings.load_all()
    watchlist_movies = watchlist.load_all()

    imdb_data.update(
        existing_imdb_ids(
            viewings_movies=viewings_movies, watchlist_movies=watchlist_movies
        )
    )
    reviews.export()
    viewings.export(viewings_movies)
    watchlist_exporter.export(watchlist_movies)
    most_watched_movies.export()
    most_watched_people.export()
