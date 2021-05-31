from movielog.reviews.exports import (
    average_grade_for_decades,
    grade_distributions,
    highest_rated_directors,
    highest_rated_performers,
    highest_rated_writers,
    review_stats,
    reviewed_movies,
)


def export() -> None:
    reviewed_movies.export()
    review_stats.export()
    average_grade_for_decades.export()
    grade_distributions.export()
    highest_rated_directors.export()
    highest_rated_performers.export()
    highest_rated_writers.export()
