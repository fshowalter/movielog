from movielog.exports.json_maybe_reviewed_title import JsonMaybeReviewedTitle


class JsonViewedTitle(JsonMaybeReviewedTitle):
    """A title that has been viewed at least once."""

    viewingDate: str  # noqa: N815
    viewingSequence: int  # noqa: N815
    medium: str | None
    venue: str | None
