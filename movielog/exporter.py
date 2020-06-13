from movielog import reviews, viewings, watchlist_titles_table


def export() -> None:
    reviews.export()
    viewings.export()
    watchlist_titles_table.export()
