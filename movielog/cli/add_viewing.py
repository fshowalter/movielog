import html
import re
from datetime import date, datetime
from typing import List, Optional, Tuple

from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.shortcuts import confirm
from prompt_toolkit.validation import Validator

from movielog import api as movielog_api
from movielog.cli import ask, radio_list, select_movie

Option = Tuple[Optional[str], AnyFormattedText]


def prompt() -> None:
    movie = select_movie.prompt()

    if not movie:
        return

    viewing_date = ask_for_date()

    if not viewing_date:
        return

    medium = ask_for_medium()

    if not medium:
        return

    grade = ask_for_grade(imdb_id=movie.imdb_id)

    if not grade:
        return

    movielog_api.add_viewing(
        imdb_id=movie.imdb_id,
        title=movie.title,
        medium=medium,
        viewing_date=viewing_date,
        year=movie.year,
        grade=grade,
    )


def is_date(text: str) -> bool:
    try:
        return bool(string_to_date(text))
    except ValueError:
        return False


def string_to_date(date_string: str) -> date:
    return datetime.strptime(date_string, "%Y-%m-%d").date()  # noqa: WPS323


def ask_for_date() -> Optional[date]:
    validator = Validator.from_callable(
        is_date,
        error_message="Must be a valid date in YYYY-MM-DD format.",
        move_cursor_to_end=True,
    )

    date_string = ask.prompt(
        "Date: ",
        rprompt="YYYY-MM-DD format.",
        validator=validator,
        default=date.today().strftime("%Y-%m-%d"),  # noqa: WPS323
    )

    if not date_string:
        return None

    viewing_date = string_to_date(date_string)

    if confirm(viewing_date.strftime("%A, %B, %-d, %Y?")):  # noqa: WPS323
        return viewing_date

    return ask_for_date()


def ask_for_medium() -> Optional[str]:
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
