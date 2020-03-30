import html
from typing import Callable, Sequence

from prompt_toolkit.formatted_text import HTML

from movielog import queries
from movielog.cli.controls import ask, radio_list

PersonSearchResults = Sequence[queries.PersonSearchResult]


def prompt(
    person_type: str, search_func: Callable[[str], PersonSearchResults],
) -> queries.PersonSearchResult:
    person = None

    while person is None:
        query = ask.prompt(f"{person_type}'s name: ")

        if query is None:
            continue

        search_results = search_func(query)

        person = radio_list.prompt(
            title=HTML(f'Results for "<cyan>{query}</cyan>":'),
            options=_build_options(search_results),
        )

    return person


def _build_options(
    search_results: PersonSearchResults,
) -> radio_list.PersonSearchOptions:
    options = radio_list.PersonSearchOptions([(None, "Search again")])

    for search_result in search_results:
        option = HTML(
            "<cyan>{0}</cyan> ({1})".format(
                search_result.name,
                ", ".join(
                    html.escape(title) for title in search_result.known_for_titles
                ),
            )
        )
        options.append((search_result, option))

    return options
