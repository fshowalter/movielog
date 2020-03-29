from movielog.internal import watchlist, watchlist_titles

Collection = watchlist.Collection


def add_collection(name: str) -> watchlist.Collection:
    collection_watchlist_item = watchlist.Collection.new(name=name)
    collection_watchlist_item.save()
    return collection_watchlist_item


def update_collection(collection: watchlist.Collection) -> watchlist.Collection:
    collection.save()
    return collection


def add_director(imdb_id: str, name: str) -> watchlist.Director:
    director_watchlist_item = watchlist.Director.new(imdb_id=imdb_id, name=name)
    director_watchlist_item.save()
    director_watchlist_item.refresh_item_titles()
    return director_watchlist_item


def add_performer(imdb_id: str, name: str) -> watchlist.Performer:
    performer_watchlist_item = watchlist.Performer.new(imdb_id=imdb_id, name=name)
    performer_watchlist_item.save()
    performer_watchlist_item.refresh_item_titles()
    return performer_watchlist_item


def add_writer(imdb_id: str, name: str) -> watchlist.Writer:
    writer_watchlist_item = watchlist.Writer.new(imdb_id=imdb_id, name=name)
    writer_watchlist_item.save()
    writer_watchlist_item.refresh_item_titles()
    return writer_watchlist_item


def update_titles_for_people() -> None:
    watchlist.Director.refresh_all_item_titles()
    watchlist.Performer.refresh_all_item_titles()
    watchlist.Writer.refresh_all_item_titles()
    watchlist_titles.update()
