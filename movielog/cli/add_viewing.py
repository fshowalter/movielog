import html
from datetime import date, datetime
from typing import Optional

from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import confirm
from prompt_toolkit.validation import Validator

from movielog import viewings
from movielog.cli import ask, radio_list, select_movie


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

    viewings.add(
        imdb_id=movie.imdb_id,
        title=movie.title,
        venue=venue,
        viewing_date=viewing_date,
        year=movie.year,
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
        "Date: ", rprompt="YYYY-MM-DD format.", validator=validator
    )
    if not date_string:
        return None

    viewing_date = string_to_date(date_string)
    if confirm(viewing_date.strftime("%A, %B, %-d, %Y?")):  # noqa: WPS323
        return viewing_date

    return ask_for_date()


def ask_for_venue() -> Optional[str]:
    venues = viewings.venues()

    options = radio_list.StringOptions([])

    for venue in venues:
        option = (venue, HTML(f"<cyan>{html.escape(venue)}</cyan>"))
        options.append(option)

    options.append((None, HTML("New venue")))

    selected_venue = None

    while selected_venue is None:

        selected_venue = radio_list.prompt(
            title=HTML("Select venue:"), options=options,
        )

        if not selected_venue:
            selected_venue = new_venue()

    if confirm(f"{selected_venue}?"):
        return selected_venue
    return None


def new_venue() -> Optional[str]:
    return ask.prompt("Venue name: ")
