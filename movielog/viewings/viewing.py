from dataclasses import dataclass
from datetime import date


@dataclass
class Viewing(object):
    sequence: int
    date: date
    imdb_id: str
    title: str
    venue: str
