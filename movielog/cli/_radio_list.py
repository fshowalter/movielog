from typing import Any, Callable, List, NewType, Optional, Sequence, Tuple, overload

from prompt_toolkit import key_binding
from prompt_toolkit.application import Application
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.widgets import Label, RadioList

from movie_db import queries, watchlist

OptionalCallableType = Optional[Callable[[], None]]
CallableOptionType = Tuple[OptionalCallableType, HTML]
CallableOptions = NewType('CallableOptions', List[CallableOptionType])

PersonSearchResultOptionType = Tuple[Optional[queries.PersonSearchResult], HTML]
PersonSearchOptions = NewType('PersonSearchOptions', List[PersonSearchResultOptionType])

CollectionOptionType = Tuple[Optional[watchlist.Collection], HTML]
CollectionOptions = NewType('CollectionOptions', List[CollectionOptionType])

MovieSearchResultOptionType = Tuple[Optional[queries.MovieSearchResult], str]
MovieSearchOptions = NewType('MovieSearchOptions', List[MovieSearchResultOptionType])

VenueOptionType = Tuple[Optional[str], HTML]
VenueOptions = NewType('VenueOptions', List[VenueOptionType])


@overload
def prompt(title: str, options: CallableOptions) -> OptionalCallableType:
    ...  # noqa: WPS428


@overload
def prompt(title: str, options: CollectionOptions) -> Optional[watchlist.Collection]:
    ...  # noqa: WPS428


@overload
def prompt(title: str, options: PersonSearchOptions) -> Optional[queries.PersonSearchResult]:
    ...  # noqa: WPS428


@overload
def prompt(title: str, options: MovieSearchOptions) -> Optional[queries.MovieSearchResult]:
    ...  # noqa: WPS428


@overload
def prompt(title: str, options: VenueOptions) -> Optional[str]:
    ...  # noqa: WPS428


def prompt(title: str, options: Sequence[Any]) -> Any:
    control = RadioList(options)

    # Add exit key binding.
    bindings = key_binding.KeyBindings()

    @bindings.add('c-d')  # type: ignore  # noqa WPS430
    def exit_(event: key_binding.key_processor.KeyPressEvent) -> None:
        """
        Pressing Ctrl-d will exit the user interface.
        """
        event.app.exit()

    @bindings.add('enter', eager=True)  # type: ignore  # noqa: WPS430
    def exit_with_value(event: key_binding.key_processor.KeyPressEvent) -> None:
        """
        Pressing Ctrl-a will exit the user interface returning the selected value.
        """
        control._handle_enter()  # noqa: WPS437
        event.app.exit(result=control.current_value)

    application = Application(
        layout=Layout(HSplit([Label(title), control])),
        key_bindings=key_binding.merge_key_bindings(
            [key_binding.defaults.load_key_bindings(), bindings],
        ),
        mouse_support=True,
        full_screen=False,
    )

    return application.run()
