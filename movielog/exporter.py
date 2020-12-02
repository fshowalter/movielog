from movielog import (
    most_watched_movies,
    most_watched_people,
    reviews,
    viewings,
    watchlist_exporter,
)


def export() -> None:
    most_watched_movies.export()
    most_watched_people.export()
    viewings.export()
    reviews.export()
    watchlist_exporter.export()
