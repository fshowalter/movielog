from movielog.exports.json_title import JsonTitle


class JsonReviewedTitle(JsonTitle):
    slug: str
    grade: str
    gradeValue: int  # noqa: N815
    gradeSequence: int  # noqa: N815
    reviewDate: str  # noqa: N815
    reviewSequence: int  # noqa: N815
