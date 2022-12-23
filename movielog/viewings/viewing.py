from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Viewing(object):
    sequence: int
    date: date
    imdb_id: str
    slug: str
    medium: Optional[str] = None
    medium_notes: Optional[str] = None
    venue: Optional[str] = None
