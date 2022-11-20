from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Review(object):
    imdb_id: str
    slug: str
    date: date
    grade: str
    review_content: Optional[str] = None

    @property
    def grade_value(self) -> Optional[int]:
        if not self.grade:
            return None

        value_modifier = 1

        grade_map = {
            "A": 12,
            "B": 9,
            "C": 6,
            "D": 3,
        }

        grade_value = grade_map.get(self.grade[0], 1)
        modifier = self.grade[-1]

        if modifier == "+":
            grade_value += value_modifier

        if modifier == "-":
            grade_value -= value_modifier

        return grade_value
