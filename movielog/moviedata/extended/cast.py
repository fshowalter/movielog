from dataclasses import dataclass
from typing import Any, Optional, Union

import imdb


@dataclass
class Credit(object):
    person_imdb_id: str
    name: str
    sequence: int
    roles: list[str]
    notes: Optional[str]


def valid_notes(credit: imdb.Person.Person) -> bool:
    notes = credit.notes.strip()
    return "uncredited" not in notes and "scenes deleted" not in notes


def parse_role(
    roles: Union[imdb.Character.Character, imdb.utils.RolesList]
) -> list[str]:
    if isinstance(roles, imdb.Character.Character):
        name = roles.get("name")
        if name:
            return [name]

        return []

    return [role["name"] for role in roles]


def parse(movie: imdb.Movie.Movie) -> list[Credit]:
    credit_list: list[Credit] = []

    for index, filtered_credit in enumerate(movie.get("cast", [])):
        if not valid_notes(filtered_credit):
            continue

        credit_list.append(
            Credit(
                sequence=index,
                person_imdb_id="nm{0}".format(filtered_credit.personID),
                name=filtered_credit["name"],
                notes=filtered_credit.notes,
                roles=parse_role(filtered_credit.currentRole),
            )
        )

    return credit_list


def deserialize(
    json_cast_credits: list[dict[str, Any]],
) -> list[Credit]:
    return [
        Credit(
            name=credit["name"],
            person_imdb_id=credit["person_imdb_id"],
            sequence=credit["sequence"],
            notes=credit["notes"],
            roles=credit["roles"],
        )
        for credit in json_cast_credits
    ]
