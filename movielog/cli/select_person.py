import html
from typing import Callable, List, Sequence, Optional, Tuple

from prompt_toolkit.formatted_text import HTML

from movielog.cli import ask, radio_list, queries

PersonSearchResults = Sequence[queries.PersonSearchResult]
Option = Tuple[Optional[queries.PersonSearchResult], str]


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


def _build_options(search_results: PersonSearchResults,) -> Sequence[Option]:
    options: List[Option] = [(None, "Search again")]

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
