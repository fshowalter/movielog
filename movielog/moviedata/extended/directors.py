from dataclasses import dataclass
from typing import Any, Optional

import imdb


@dataclass
class Credit(object):
    person_imdb_id: str
    name: str
    sequence: int
    notes: Optional[str]


def valid_notes(credit: imdb.Movie.Movie) -> bool:
    return "scenes deleted" not in credit.notes


def parse(movie: imdb.Movie.Movie) -> list[Credit]:
    credit_list: list[Credit] = []

    imdb_credits = movie.get("directors", [])

    for index, credit in enumerate(imdb_credits):
        if not valid_notes(credit):
            continue

        credit_list.append(
            Credit(
                person_imdb_id="nm{0}".format(credit.personID),
                name=credit["name"],
                notes=credit.notes,
                sequence=index,
            )
        )

    return credit_list


def deserialize(
    json_directing_credits: list[dict[str, Any]],
) -> list[Credit]:
    return [
        Credit(
            name=credit["name"],
            person_imdb_id=credit["person_imdb_id"],
            sequence=credit["sequence"],
            notes=credit["notes"],
        )
        for credit in json_directing_credits
    ]
