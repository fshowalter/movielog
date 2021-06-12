from datetime import date
from typing import Sequence

from movielog.reviews import serializer
from movielog.reviews.review import Review

RECENT_DAYS = 365


def review_is_recent(review: Review) -> bool:
    return (date.today() - review.date).days < RECENT_DAYS


def recent() -> Sequence[str]:
    recent_reviews = filter(review_is_recent, serializer.deserialize_all())

    return sorted(set([review.venue for review in recent_reviews]))
