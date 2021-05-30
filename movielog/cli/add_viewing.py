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

    venue = ask_for_venue()

    if not venue:
        return

    grade = ask_for_grade(imdb_id=movie.imdb_id)

    if not grade:
        return

    movielog_api.create_viewing(
        imdb_id=movie.imdb_id,
        title=movie.title,
        venue=venue,
        viewing_date=viewing_date,
        year=movie.year,
    )

    movielog_api.create_review(
        imdb_id=movie.imdb_id,
        title=movie.title,
        venue=venue,
        review_date=viewing_date,
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


def ask_for_venue() -> Optional[str]:
    options: List[Option] = build_venue_options()

    selected_venue = None

    while selected_venue is None:

        selected_venue = radio_list.prompt(
            title="Select venue:",
            options=options,
        )

        selected_venue = selected_venue or new_venue()

        if selected_venue is None:
            break

    if not selected_venue:
        return None

    if confirm(f"{selected_venue}?"):
        return selected_venue

    return ask_for_venue()


def build_venue_options() -> List[Option]:
    venues = movielog_api.venues()

    options: List[Option] = []

    for venue in venues:
        option = (venue, "<cyan>{0}</cyan>".format(html.escape(venue)))
        options.append(option)

    options.append((None, "New venue"))

    return options


def new_venue() -> Optional[str]:
    return ask.prompt("Venue name: ")


def is_grade(text: str) -> bool:
    return bool(re.match("[a-d|A-D|f|F][+|-]?", text))


def ask_for_grade(imdb_id: str) -> Optional[str]:
    validator = Validator.from_callable(
        is_grade,
        error_message="Must be a valid grade.",
        move_cursor_to_end=True,
    )

    default_grade = ""

    review_grade = ask.prompt("Grade: ", validator=validator, default=default_grade)

    if not review_grade:
        return None

    if confirm(review_grade):  # noqa: WPS323
        return review_grade

    return ask_for_grade(imdb_id=imdb_id)
