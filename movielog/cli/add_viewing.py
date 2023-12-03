import datetime
import html
import re
from dataclasses import dataclass, field
from typing import Callable, List, Literal, Optional, Tuple

from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.shortcuts import confirm
from prompt_toolkit.validation import Validator

from movielog.cli import ask, radio_list, select_title
from movielog.repository import api as repository_api

Option = Tuple[Optional[str], AnyFormattedText]

Stages = Literal[
    "ask_for_title",
    "ask_for_date",
    "ask_for_medium_or_venue",
    "ask_for_grade",
    "persist_viewing",
    "end",
]


@dataclass(kw_only=True)
class State(object):
    stage: Stages = "ask_for_title"
    title: Optional[repository_api.Title] = None
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
        "ask_for_venue": ask_for_venue,
        "ask_for_grade": ask_for_grade,
        "persist_viewing": persist_viewing,
    }

    while state.stage != "end":
        state_machine[state.stage](state)


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

    state.date = string_to_date(date_string)
    return state


def ask_for_medium(state: State) -> State:
    state.medium = None

    options: List[Option] = build_medium_options()

    selected_medium = None

    while selected_medium is None:
        selected_medium = radio_list.prompt(
            title="Select medium:",
            options=options,
        )

        selected_medium = selected_medium or new_medium()

        if selected_medium is None:
            break

    if not selected_medium:
        return None

    if confirm("{0}?".format(selected_medium)):
        return selected_medium

    return ask_for_medium()


def build_medium_options() -> List[Option]:
    media = movielog_api.recent_media()

    options: List[Option] = []

    for medium in media:
        option = (medium, "<cyan>{0}</cyan>".format(html.escape(medium)))
        options.append(option)

    options.append((None, "New medium"))

    return options


def new_medium() -> Optional[str]:
    return ask.prompt("Medium name: ")


def is_grade(text: str) -> bool:
    if not text:
        return True

    return bool(re.match("[a-d|A-D|f|F][+|-]?", text))


def ask_for_grade(imdb_id: str) -> Optional[str]:
    validator = Validator.from_callable(
        is_grade,
        error_message="Must be a valid grade.",
        move_cursor_to_end=True,
    )

    existing_review = movielog_api.review_for_movie(imdb_id)

    default_grade = existing_review.grade if existing_review else ""

    review_grade = ask.prompt("Grade: ", validator=validator, default=default_grade)

    if not review_grade:
        return None

    if confirm(review_grade):  # noqa: WPS323
        return review_grade

    return ask_for_grade(imdb_id=imdb_id)
