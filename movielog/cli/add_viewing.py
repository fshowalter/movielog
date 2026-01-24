import datetime
import html
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Literal

from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.shortcuts import confirm
from prompt_toolkit.validation import Validator

from movielog.cli import (
    ask,
    ask_for_token,
    ask_medium_or_venue,
    ask_review,
    radio_list,
    select_title,
)
from movielog.repository import api as repository_api

Option = tuple[str | None, AnyFormattedText]

Stages = Literal[
    "ask_for_title",
    "ask_for_date",
    "ask_if_medium_or_venue",
    "ask_for_medium",
    "ask_for_medium_notes",
    "ask_for_venue",
    "ask_create_review",
    "ask_for_grade",
    "persist_viewing",
    "end",
]


@dataclass(kw_only=True)
class State:
    stage: Stages = "ask_for_title"
    title: select_title.SearchResult | None = None
    date: datetime.date | None = None
    medium: str | None = None
    medium_notes: str | None = None
    venue: str | None = None
    grade: str | None = None
    default_date: datetime.date = field(default_factory=datetime.date.today)
    existing_review: repository_api.Review | None = None


def prompt() -> None:
    state = State()

    state_machine: dict[Stages, Callable[[State], State]] = {
        "ask_for_title": ask_for_title,
        "ask_for_date": ask_for_date,
        "ask_if_medium_or_venue": ask_if_medium_or_venue,
        "ask_for_medium": ask_for_medium,
        "ask_for_medium_notes": ask_for_medium_notes,
        "ask_for_venue": ask_for_venue,
        "ask_for_grade": ask_for_grade,
        "ask_create_review": ask_create_review,
        "persist_viewing": persist_viewing,
    }

    while state.stage != "end":
        state = state_machine[state.stage](state)


def persist_viewing(state: State) -> State:
    assert state.title
    assert state.date
    assert state.medium or state.venue

    repository_api.create_viewing(
        imdb_id=state.title.imdb_id,
        full_title=state.title.full_title,
        date=state.date,
        medium=state.medium,
        venue=state.venue,
        medium_notes=state.medium_notes,
    )

    if state.grade:
        repository_api.create_or_update_review(
            imdb_id=state.title.imdb_id,
            full_title=state.title.full_title,
            date=state.date,
            grade=state.grade,
        )

    if confirm("Add another viewing?"):
        state = State()
    else:
        state.stage = "end"

    return state


def ask_for_title(state: State) -> State:
    state.title = None

    token = ask_for_token.prompt()

    if not token:
        state.stage = "end"
        return state

    title = select_title.prompt(token)

    if not token:
        state.stage = "end"
        return state

    state.title = title
    state.stage = "ask_for_date"
    return state


def is_date(text: str) -> bool:
    try:
        return bool(string_to_date(text))
    except ValueError:
        return False


def string_to_date(date_string: str) -> datetime.date:
    return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()


def ask_for_date(state: State) -> State:
    state.date = None

    validator = Validator.from_callable(
        is_date,
        error_message="Must be a valid date in YYYY-MM-DD format.",
        move_cursor_to_end=True,
    )

    date_string = ask.prompt(
        "Date: ",
        rprompt="YYYY-MM-DD format.",
        validator=validator,
        default=state.default_date.strftime("%Y-%m-%d"),
    )

    if not date_string:
        state.stage = "ask_for_title"
        return state

    viewing_date = string_to_date(date_string)

    if confirm(viewing_date.strftime("%A, %B, %-d, %Y?")):
        state.date = viewing_date
        state.default_date = viewing_date
        state.stage = "ask_if_medium_or_venue"

    return state


def ask_for_medium(state: State) -> State:
    state.medium = None

    options = build_medium_options()

    selected_medium = None

    while selected_medium is None:
        selected_medium = radio_list.prompt(
            title="Select medium:",
            options=options,
        )

        selected_medium = selected_medium or ask.prompt("Medium: ")

        if selected_medium is None:
            break

    if not selected_medium:
        state.stage = "ask_if_medium_or_venue"
        return state

    state.medium = selected_medium
    state.stage = "ask_for_medium_notes"

    return state


def ask_for_venue(state: State) -> State:
    state.venue = None

    options = build_venue_options()

    selected_venue = None

    while selected_venue is None:
        selected_venue = radio_list.prompt(
            title="Select venue:",
            options=options,
        )

        selected_venue = selected_venue or ask.prompt("Venue: ")

        if selected_venue is None:
            break

    if not selected_venue:
        state.stage = "ask_if_medium_or_venue"
        return state

    state.venue = selected_venue
    state.stage = "ask_create_review"

    return state


def sorted_viewings() -> list[repository_api.Viewing]:
    return sorted(
        repository_api.viewings(),
        key=lambda viewing: f"{viewing.date.isoformat()}-{viewing.sequence}",
        reverse=True,
    )


def build_medium_options() -> list[Option]:
    media: set[str] = set()

    for viewing in sorted_viewings():
        if len(media) == 10:
            break

        if viewing.medium:
            media.add(viewing.medium)

    options: list[Option] = [
        (medium, f"<cyan>{html.escape(medium)}</cyan>") for medium in sorted(media)
    ]

    options.append((None, "New medium"))

    return options


def build_venue_options() -> list[Option]:
    venues: set[str] = set()

    for viewing in sorted_viewings():
        if len(venues) == 2:
            break

        if viewing.venue:
            venues.add(viewing.venue)

    options: list[Option] = [
        (medium, f"<cyan>{html.escape(medium)}</cyan>") for medium in sorted(venues)
    ]

    options.append((None, "New venue"))

    return options


def is_grade(text: str) -> bool:
    if not text:
        return True

    return bool(re.match(r"[a-dA-DfF][+\-]?", text))


def ask_for_medium_notes(state: State) -> State:
    state.medium_notes = None

    state.medium_notes = ask.prompt("Medium Notes: ")

    if state.medium_notes is None:
        state.stage = "ask_for_medium"
    else:
        state.stage = "ask_create_review"

    return state


def ask_create_review(state: State) -> State:
    assert state.title

    state.existing_review = next(
        (review for review in repository_api.reviews() if review.imdb_id == state.title.imdb_id),
        None,
    )

    if state.existing_review:
        state.stage = "ask_for_grade"
        return state

    create_review = ask_review.ask_review()

    if create_review == "y":
        state.stage = "ask_for_grade"
        return state

    if create_review == "n":
        state.stage = "persist_viewing"
        return state

    if state.medium_notes:
        state.stage = "ask_for_medium_notes"
        return state

    if state.medium:
        state.stage = "ask_for_medium"
        return state

    state.stage = "ask_for_venue"
    return state


def ask_for_grade(state: State) -> State:
    state.grade = None

    validator = Validator.from_callable(
        is_grade,
        error_message="Must be a valid grade.",
        move_cursor_to_end=True,
    )

    default_grade = state.existing_review.grade if state.existing_review else ""

    review_grade = ask.prompt("Grade: ", validator=validator, default=default_grade)

    if not review_grade:
        state.stage = "ask_if_medium_or_venue"
        state.grade = None
        return state

    state.grade = review_grade
    state.stage = "persist_viewing"
    return state


def ask_if_medium_or_venue(state: State) -> State:
    state.venue = None
    state.medium = None

    medium_or_venue = ask_medium_or_venue.ask_medium_or_venue()

    if medium_or_venue == "m":
        state.stage = "ask_for_medium"
        return state

    if medium_or_venue == "v":
        state.stage = "ask_for_venue"
        return state

    state.stage = "ask_for_date"
    return state
