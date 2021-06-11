from movielog.moviedata import api as moviedata_api
from movielog.reviews import api as reviews_api
from movielog.viewings import api as viewings_api
from movielog.watchlist import api as watchlist_api

Collection = watchlist_api.Collection

# viewing methods

create_viewing = viewings_api.create

active_venues = viewings_api.active_venues

# review methods

create_review = reviews_api.create

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
    viewing_imdb_ids = set([movie.imdb_id for movie in viewings_api.viewings()])
    watchlist_imdb_ids = set([movie.imdb_id for movie in watchlist_api.movies()])

    moviedata_api.update_extended_data(viewing_imdb_ids.union(watchlist_imdb_ids))
    reviews_api.export_data()
    viewings_api.export_data()
    watchlist_api.export_data()
