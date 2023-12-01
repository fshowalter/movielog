from movielog.watchlist.exports import watchlist_entities, watchlist_movies


def export() -> None:
    watchlist_movies.export()
    watchlist_entities.export()
