from movielog.moviedata import api as moviedata_api
from movielog.reviews import api as reviews_api
from movielog.watchlist import api as watchlist_api

Collection = watchlist_api.Collection

# review methods

create_review = reviews_api.create

recent_venues = reviews_api.recent_venues

most_recent_review_for_movie = reviews_api.most_recent_review_for_movie

# moviedata methods

refresh_core_data = moviedata_api.refresh_core_data

# watchlist methods

add_director = watchlist_api.add_director

add_performer = watchlist_api.add_performer

add_writer = watchlist_api.add_writer

collections = watchlist_api.collections

refresh_credits = watchlist_api.refresh_credits

add_collection = watchlist_api.add_collection

add_movie_to_collection = watchlist_api.add_movie_to_collection


def export_data() -> None:
    moviedata_api.update_extended_data(
        watchlist_api.movie_ids().union(reviews_api.movie_ids())
    )
    watchlist_api.export_data()
    reviews_api.export_data()
