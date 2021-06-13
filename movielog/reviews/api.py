from __future__ import annotations

from datetime import date

from slugify import slugify

from movielog.reviews import reviews_table, serializer, venues, viewings, viewings_table
from movielog.reviews.exports import api as exports_api
from movielog.reviews.review import Review
from movielog.utils import sequence_tools

save = serializer.serialize

recent_venues = venues.recent


def export_data() -> None:
    reviews = serializer.deserialize_all()
    viewings_table.update([*viewings.deserialize_all(), *reviews])
    reviews_table.update(reviews)
    exports_api.export()


def movie_ids() -> set[str]:
    return set(
        [
            *[review.imdb_id for review in serializer.deserialize_all()],
            *[viewing.imdb_id for viewing in viewings.deserialize_all()],
        ]
    )


def create(  # noqa: WPS211
    review_date: date, imdb_id: str, title: str, year: int, grade: str, venue: str
) -> Review:
    sequence = sequence_tools.next_sequence(
        [*viewings.deserialize_all(), *serializer.deserialize_all()]
    )
    review_title = "{0} ({1})".format(title, year)
    slug = slugify(review_title, replacements=[("'", "")])

    review = Review(
        sequence=sequence,
        slug=slug,
        date=review_date,
        title=review_title,
        imdb_id=imdb_id,
        grade=grade,
        venue=venue,
    )

    save(review)

    return review
