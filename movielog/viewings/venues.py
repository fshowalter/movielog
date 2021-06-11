from typing import Sequence

from movielog.viewings import serializer

INACTIVE_VENUES = (
    "AFI Silver",
    "AMC Tysons Corner",
    "Alamo Drafthouse Cinema - Winchester",
    "Alamo Drafthouse Cinema - Woodbridge",
    "Angelika Film Center Mosaic",
    "Arte",
    "Encore HD",
    "FXM",
    "HBO GO",
    "HBO HD",
    "HDNet",
    "Landmark E Street Cinema",
    "Prince Charles Cinema",
    "Sun & Surf Cinema",
    "TCM",
    "The Black Cat",
)


def active() -> Sequence[str]:
    all_venues = sorted(
        set([viewing.venue for viewing in serializer.deserialize_all()])
    )

    return list(filter(lambda venue: venue not in INACTIVE_VENUES, all_venues))
