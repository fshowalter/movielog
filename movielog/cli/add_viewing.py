import datetime
import html
import re
from dataclasses import dataclass, field
from typing import Callable, Literal, Optional, Tuple

from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.shortcuts import confirm
from prompt_toolkit.validation import Validator

from movielog.cli import ask, radio_list, select_title
from movielog.repository import api as repository_api

RECENT_VIEWING_DAYS = 365


Option = Tuple[Optional[str], AnyFormattedText]

Stages = Literal[
    "ask_for_title",
    "ask_for_date",
    "ask_for_medium",
    "ask_for_grade",
    "persist_viewing",
    "end",
]


@dataclass(kw_only=True)
class State(object):
    stage: Stages = "ask_for_title"
    title: Optional[select_title.SearchResult] = None
    date: Optional[datetime.date] = None
    medium: Optional[str] = None
    venue: Optional[str] = None
    grade: Optional[str] = None
    default_date: datetime.date = field(default_factory=datetime.date.today)


def prompt() -> None:
    state = State()

    state_machine: dict[Stages, Callable[[State], State]] = {
        "ask_for_title": ask_for_title,
        "ask_for_date": ask_for_date,
        "ask_for_medium": ask_for_medium,
        "ask_for_grade": ask_for_grade,
        "persist_viewing": persist_viewing,
    }

    while state.stage != "end":
        state_machine[state.stage](state)


def persist_viewing(state: State) -> State:
    assert state.title
    assert state.date
    assert state.medium
    assert state.grade

    repository_api.create_viewing(
        imdb_id=state.title.imdb_id,
        full_title=state.title.full_title,
        date=state.date,
        medium=state.medium,
    )

    repository_api.create_or_update_review(
        imdb_id=state.title.imdb_id,
        full_title=state.title.full_title,
        date=state.date,
        grade=state.grade,
    )

    if confirm("Add another viewing?"):
        state.stage = "ask_for_title"
    else:
        state.stage = "end"

    return state


def ask_for_title(state: State) -> State:
    state.title = None

    title = select_title.prompt()

    if not title:
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
        default=state.default_date.strftime("%Y-%m-%d"),  # noqa: WPS323
    )

    if not date_string:
        state.stage = "ask_for_title"
        return state

    viewing_date = string_to_date(date_string)

    if confirm(viewing_date.strftime("%A, %B, %-d, %Y?")):  # noqa: WPS323
        state.date = viewing_date
        state.default_date = viewing_date
        state.stage = "ask_for_medium"

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
        state.stage = "ask_for_date"
        return state

    state.medium = selected_medium
    state.stage = "ask_for_grade"

    return state


def build_medium_options() -> list[Option]:
    media = sorted(
        set(
            [
                viewing.medium
                for viewing in repository_api.viewings()
                if (datetime.date.today() - viewing.date).days < RECENT_VIEWING_DAYS
                and viewing.medium
            ]
        )
    )

    options: list[Option] = [
        (medium, "<cyan>{0}</cyan>".format(html.escape(medium))) for medium in media
    ]

    options.append((None, "New medium"))

    return options


def is_grade(text: str) -> bool:
    if not text:
        return True

    return bool(re.match("[a-d|A-D|f|F][+|-]?", text))


def ask_for_grade(state: State) -> State:
    state.grade = None

    validator = Validator.from_callable(
        is_grade,
        error_message="Must be a valid grade.",
        move_cursor_to_end=True,
    )

    assert state.title

    existing_review = next(
        (
            review
            for review in repository_api.reviews()
            if review.imdb_id == state.title.imdb_id
        ),
        None,
    )

    default_grade = existing_review.grade if existing_review else ""

    review_grade = ask.prompt("Grade: ", validator=validator, default=default_grade)

    if not review_grade:
        state.stage = "ask_for_medium"
        state.grade = None
        return state

    state.grade = review_grade
    state.stage = "persist_viewing"
    return state
