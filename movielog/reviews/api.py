from __future__ import annotations

from datetime import date
from typing import Optional

from movielog.reviews import reviews_table, serializer
from movielog.reviews.exports import api as exports_api
from movielog.reviews.review import Review


def review_for_movie(imdb_id: str) -> Optional[Review]:
    all_reviews = serializer.deserialize_all()
    filtered_reviews = filter(lambda review: review.imdb_id == imdb_id, all_reviews)
    return next(filtered_reviews, None)


def export_data() -> None:
    reviews_table.update(serializer.deserialize_all())
    exports_api.export()


def create_or_update(review_date: date, imdb_id: str, slug: str, grade: str) -> Review:
    existing_review = review_for_movie(imdb_id=imdb_id)

    if existing_review:
        existing_review.grade = grade
        serializer.serialize(existing_review)
        return existing_review

    new_review = Review(
        slug=slug,
        date=review_date,
        imdb_id=imdb_id,
        grade=grade,
    )

    serializer.serialize(new_review)

    return new_review
