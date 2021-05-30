from datetime import date
from typing import Sequence

from movielog.utils import sequence_tools
from movielog.viewings import serializer, viewings_table
from movielog.viewings.exports import api as exports_api
from movielog.viewings.viewing import Viewing


def save(viewing: Viewing) -> str:
    return serializer.serialize(viewing)


def viewings() -> Sequence[Viewing]:
    return serializer.deserialize_all()


def venues() -> Sequence[str]:
    return sorted(set([viewing.venue for viewing in viewings()]))


def export_data() -> None:
    exports_api.export()


def create(
    imdb_id: str, title: str, venue: str, viewing_date: date, year: str
) -> Viewing:
    viewing_title = "{0} ({1})".format(title, year)
    sequence = sequence_tools.next_sequence(viewings())
    viewing = Viewing(
        imdb_id=imdb_id,
        title=viewing_title,
        venue=venue,
        date=viewing_date,
        sequence=sequence,
    )

    save(viewing)

    viewings_table.add_row(
        viewings_table.Row(
            movie_imdb_id=viewing.imdb_id,
            date=viewing.date,
            sequence=viewing.sequence,
            venue=viewing.venue,
        )
    )

    return viewing
