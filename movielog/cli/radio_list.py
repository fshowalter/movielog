from typing import Any, Callable, List, NewType, Optional, Sequence, Tuple, overload

from prompt_toolkit import key_binding
from prompt_toolkit.application import Application
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.widgets import Label, RadioList

# from movielog import watchlist_collection
from movielog.cli import movie_searcher

OptionalCallableType = Optional[Callable[[], None]]
CallableOptionType = Tuple[OptionalCallableType, HTML]
CallableOptions = NewType("CallableOptions", List[CallableOptionType])

# PersonSearchResultOptionType = Tuple[Optional[queries.PersonSearchResult], HTML]
# PersonSearchOptions = NewType("PersonSearchOptions", List[PersonSearchResultOptionType])

# CollectionOptionType = Tuple[Optional[watchlist_collection.Collection], HTML]
# CollectionOptions = NewType("CollectionOptions", List[CollectionOptionType])

MovieSearchResultOptionType = Tuple[Optional[movie_searcher.Result], str]
MovieSearchOptions = NewType("MovieSearchOptions", List[MovieSearchResultOptionType])

StringOptionType = Tuple[Optional[str], HTML]
StringOptions = NewType("StringOptions", List[StringOptionType])


@overload
def prompt(title: str, options: CallableOptions) -> OptionalCallableType:
    """ Radio list prompt that returns a callable or None. """


# @overload
# def prompt(
#     title: str, options: CollectionOptions
# ) -> Optional[watchlist_collection.Collection]:
#     ...  # noqa: WPS428


# @overload
# def prompt(
#     title: str, options: PersonSearchOptions
# ) -> Optional[queries.PersonSearchResult]:
#     ...  # noqa: WPS428


@overload
def prompt(title: str, options: MovieSearchOptions) -> Optional[movie_searcher.Result]:
    """ Radio list prompt that returns a movie_searcher result or None. """


@overload
def prompt(title: str, options: StringOptions) -> Optional[str]:
    """ Radio list prompt that returns a str result or None. """


def prompt(title: str, options: Sequence[Any]) -> Any:
    control = RadioList(options)

    # Add exit key binding.
    bindings = key_binding.KeyBindings()

    @bindings.add("c-d")  # type: ignore  # noqa WPS430
    def exit_(event: key_binding.key_processor.KeyPressEvent) -> None:
        """
        Pressing Ctrl-d will exit the user interface.
        """
        event.app.exit()

    @bindings.add("enter", eager=True)  # type: ignore  # noqa: WPS430
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
