from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Review(object):
    sequence: int
    imdb_id: str
    title: str
    date: date
    grade: str
    venue: str
    slug: str
    venue_notes: Optional[str] = None
    review_content: Optional[str] = None

    @property
    def grade_value(self) -> float:
        if not self.grade:
            return 0

        value_modifier = 0.33

        grade_map = {
            "A": 5.0,
            "B": 4.0,
            "C": 3.0,
            "D": 2.0,
            "F": 1.0,
        }

        grade_value = grade_map.get(self.grade[0], 3)
        modifier = self.grade[-1]

        if modifier == "+":
            grade_value += value_modifier

        if modifier == "-":
            grade_value -= value_modifier

        return grade_value
