import re

from movielog.repository import imdb_http_title

INVALID_WRITER_NOTES = (
    "uncredited",
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

INVALID_DIRECTOR_NOTES = ("scenes delted", "uncredited")


INVALID_PERRFORMER_NOTES = ("uncredited", "scenes deleted", "voice", "archiveFootage")


def _validate_director_credit_notes(notes: str) -> tuple[bool, str | None]:
    if any(invalid_note in notes for invalid_note in INVALID_DIRECTOR_NOTES):
        return (False, notes)

    return (True, None)


def _validate_performer_credit_notes(notes: str) -> tuple[bool, str | None]:
    if any(invalid_note in notes for invalid_note in INVALID_PERRFORMER_NOTES):
        return (False, notes)

    return (True, None)


def _validate_writer_credit_notes(notes: str) -> tuple[bool, str | None]:
    if any(invalid_note in notes for invalid_note in INVALID_WRITER_NOTES):
        return (False, notes)

    if CREATED_BY_REGEX.match(notes):
        return (False, notes)

    if CHARACTER_CREATED_BY_REGEX.match(notes):
        return (False, notes)

    return (True, None)


def credit_notes_are_valid_for_kind(
    notes: str | None, kind: imdb_http_title.CreditKind
) -> tuple[bool, str | None]:
    if not notes:
        return (True, None)

    match kind:
        case "director":
            return _validate_director_credit_notes(notes)
        case "performer":
            return _validate_performer_credit_notes(notes)
        case "writer":
            return _validate_writer_credit_notes(notes)
