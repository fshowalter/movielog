from datetime import date
from typing import Sequence

from movielog.viewings import serializer
from movielog.viewings.viewing import Viewing

RECENT_DAYS = 365


def viewing_is_recent(viewing: Viewing) -> bool:
    return (date.today() - viewing.date).days < RECENT_DAYS


def recent() -> Sequence[str]:
    recent_viewings = filter(viewing_is_recent, serializer.deserialize_all())

    return sorted(set([viewing.venue for viewing in recent_viewings]))
