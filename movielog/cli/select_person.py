import html
from typing import Callable, List, Optional, Sequence, Tuple

from prompt_toolkit.formatted_text import AnyFormattedText

from movielog.cli import ask, confirm, person_searcher, radio_list

Result = person_searcher.Result
Option = Tuple[Optional[Result], AnyFormattedText]


def prompt(search_func: Callable[[str], Sequence[Result]]) -> Optional[Result]:
    person = None

    while person is None:
        query = ask.prompt(f"Name: ", rprompt="Use ^ and $ to anchor")

        if query is None:
            break

        search_results = search_func(query)

        person = radio_list.prompt(
            title=f'Results for "<cyan>{query}</cyan>":',
            options=build_options(search_results),
        )

    if not person:
        return None

    if confirm.prompt(f"<cyan>{person.name}</cyan>?"):
        return person

    return prompt(search_func)


def result_to_html_string(search_result: Result) -> str:
    return "<cyan>{0}</cyan> ({1})".format(
        html.escape(search_result.name),
        ", ".join(html.escape(title) for title in search_result.known_for_titles),
    )


def build_options(search_results: Sequence[Result]) -> Sequence[Option]:
    options: List[Option] = [(None, "Search again")]

    for search_result in search_results:
        option = result_to_html_string(search_result)
        options.append((search_result, option))

    return options
