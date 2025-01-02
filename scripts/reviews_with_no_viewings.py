from movielog.repository import api as repository_api
from movielog.utils import list_tools
from movielog.utils.logging import logger


def reports_with_no_viewings() -> None:
    logger.log("Initializing...")

    reviews = sorted(repository_api.reviews(), key=lambda review: review.slug)

    viewing_dates = list_tools.group_list_by_key(
        repository_api.viewings(), key=lambda viewing: viewing.date
    )

    for review in reviews:
        if review.date not in viewing_dates.keys():
            logger.log(review.slug)
            continue

        viewing_imdb_ids = [viewing.imdb_id for viewing in viewing_dates[review.date]]

        if review.imdb_id not in viewing_imdb_ids:
            logger.log(review.slug)


if __name__ == "__main__":
    reports_with_no_viewings()
