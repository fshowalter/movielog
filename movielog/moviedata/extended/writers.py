from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Optional

import imdb

INVALID_NOTES = (
    "(based on characters created by)",
    "(character)",
    "(characters)",
    "(characters) (uncredited)",
    '("Alien" characters)',
    "(based on the Marvel comics by)",
    "(based on characters created by)",
    "(based on elements created by)",
    "(based on characters by - uncredited)",
    "(excerpt)",
    "(comic book)",
    "(comic book) (uncredited)",
    "(Marvel comic book)",
    "(trading card series)",
    "(trading card series) (as Norm Saunders)",
)

CREATED_BY_REGEX = re.compile(r"^\(.*created by\)( and)?$")
CHARACTER_CREATED_BY_REGEX = re.compile(r"\(character created by: (?:.*)\)$")


@dataclass
class Credit(object):
    person_imdb_id: str
    name: str
    group: int
    sequence: int
    notes: Optional[str]


def valid_notes(credit: imdb.Person.Person) -> bool:
    notes = credit.notes.strip()
    return (
        "(uncredited)" not in notes
        and notes not in INVALID_NOTES
        and not CREATED_BY_REGEX.match(notes)
        and not CHARACTER_CREATED_BY_REGEX.match(notes)
    )


def parse(movie: imdb.Movie.Movie) -> list[Credit]:
    credit_list: list[Credit] = []

    imdb_credits = movie.get("writers", [])
    credit_sequence = 0
    credit_group = 0

    for credit in imdb_credits:
        if not credit.keys():
            credit_group += 1
            credit_sequence = 0
            continue

        if not valid_notes(credit):
            continue

        credit_list.append(
            Credit(
                person_imdb_id="nm{0}".format(credit.personID),
                name=credit["name"],
                notes=credit.notes,
                group=credit_group,
                sequence=credit_sequence,
            )
        )

        credit_sequence += 1

    return credit_list


def deserialize(
    json_writing_credits: list[dict[str, Any]],
) -> list[Credit]:
    return [
        Credit(
            name=credit["name"],
            person_imdb_id=credit["person_imdb_id"],
            sequence=credit["sequence"],
            notes=credit["notes"],
            group=credit["group"],
        )
        for credit in json_writing_credits
    ]
