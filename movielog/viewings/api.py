from __future__ import annotations

from datetime import date

from movielog.utils import sequence_tools
from movielog.viewings import media, serializer, viewings_table
from movielog.viewings.exports import api as exports_api
from movielog.viewings.viewing import Viewing

recent_media = media.recent


def movie_ids() -> set[str]:
    return set([viewing.imdb_id for viewing in serializer.deserialize_all()])


def create(  # noqa: WPS211
    viewing_date: date, imdb_id: str, slug: str, medium: str
) -> Viewing:
    sequence = sequence_tools.next_sequence(serializer.deserialize_all())

    viewing = Viewing(
        sequence=sequence,
        date=viewing_date,
        slug=slug,
        imdb_id=imdb_id,
        medium=medium,
    )

    serializer.serialize(viewing)

    return viewing


def export_data() -> None:
    viewings_table.update(serializer.deserialize_all())
    exports_api.export()
