from movielog.exports.json_title import JsonTitle


class JsonMaybeReviewedTitle(JsonTitle):
    slug: str | None
    grade: str | None
    gradeValue: int | None  # noqa: N815
    gradeSequence: int | None  # noqa: N815
    reviewDate: str | None  # noqa: N815
    reviewSequence: int | None  # noqa: N815
