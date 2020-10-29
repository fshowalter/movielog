from movielog import most_watched, reviews, viewings, watchlist_titles_table


def export() -> None:
    most_watched.export()
    viewings.export()
    reviews.export()
    watchlist_titles_table.export()
