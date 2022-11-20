from datetime import date

from slugify import slugify

from movielog.moviedata import api as moviedata_api
from movielog.reviews import api as reviews_api
from movielog.viewings import api as viewings_api
from movielog.watchlist import api as watchlist_api

Collection = watchlist_api.Collection

# review methods

review_for_movie = reviews_api.review_for_movie

# viewing methods

recent_media = viewings_api.recent_media

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


def add_viewing(
    imdb_id: str,
    viewing_date: date,
    title: str,
    year: int,
    medium: str,
    grade: str,
) -> None:
    title_with_year = "{0} ({1})".format(title, year)
    slug = slugify(title_with_year, replacements=[("'", "")])

    viewings_api.create(
        imdb_id=imdb_id,
        viewing_date=viewing_date,
        slug=slug,
        medium=medium,
    )

    reviews_api.create_or_update(
        review_date=viewing_date, imdb_id=imdb_id, slug=slug, grade=grade
    )


def export_data() -> None:
    watchlist_movie_ids = watchlist_api.movie_ids()
    moviedata_api.update_extended_data(
        watchlist_movie_ids.union(viewings_api.movie_ids())
    )
    reviews_api.export_data(watchlist_movie_ids)
    watchlist_api.export_data()
    viewings_api.export_data()
