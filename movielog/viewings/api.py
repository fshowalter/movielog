from datetime import date

from movielog.utils import sequence_tools
from movielog.viewings import serializer, venues, viewings_table
from movielog.viewings.exports import api as exports_api
from movielog.viewings.viewing import Viewing

save = serializer.serialize

viewings = serializer.deserialize_all

export_data = exports_api.export

recent_venues = venues.recent


def create(
    imdb_id: str, title: str, venue: str, viewing_date: date, year: int
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
