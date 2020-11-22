from movielog import (
    most_watched_movies,
    most_watched_people,
    reviews,
    viewings,
    watchlist_titles_table,
)


def export() -> None:
    most_watched_movies.export()
    most_watched_people.export()
    viewings.export()
    reviews.export()
    watchlist_titles_table.export()
