from datetime import date
from typing import Sequence

from slugify import slugify

from movielog.reviews import reviews_table, serializer
from movielog.reviews.exports import api as exports_api
from movielog.reviews.review import Review
from movielog.utils import sequence_tools


def reviews() -> Sequence[Review]:
    return serializer.deserialize_all()


def save(review: Review) -> str:
    return serializer.serialize(review)


def export_data() -> None:
    exports_api.export()


def create(  # noqa: WPS211
    review_date: date, imdb_id: str, title: str, year: int, grade: str, venue: str
) -> Review:
    sequence = sequence_tools.next_sequence(reviews())
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

    reviews_table.add_row(
        reviews_table.Row(
            movie_imdb_id=review.imdb_id,
            date=review.date,
            sequence=review.sequence,
            grade=review.grade,
            grade_value=review.grade_value,
            slug=review.slug,
            venue=review.venue,
        )
    )

    return review
