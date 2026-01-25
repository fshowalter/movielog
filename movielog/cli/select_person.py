import html
from collections.abc import Iterable

from prompt_toolkit.formatted_text import HTML, AnyFormattedText
from prompt_toolkit.shortcuts import confirm

from movielog.cli import ask, ask_for_token, person_searcher, radio_list

SearchResult = person_searcher.SearchResult
Option = tuple[SearchResult | None, AnyFormattedText]


def prompt(prompt_text: str = "IMDb ID: ") -> SearchResult | None:
    token = ask_for_token.prompt()

    if not token:
        return None

    while True:
        query = ask.prompt(prompt_text)

        if query is None:
            return None

        search_results = person_searcher.search_by_name(token, query)
        options = build_options(search_results)

        selected_person = radio_list.prompt(
            title=f'Results for "<cyan>{query}</cyan>":',
            options=options,
        )

        if selected_person is None:
            continue

        if confirm(HTML(f"{result_to_html_string(selected_person)}?")):
            return selected_person


def result_to_html_string(search_result: SearchResult) -> str:
    return "<cyan>{}</cyan> ({})".format(
        html.escape(search_result.name),
        ", ".join(html.escape(title) for title in search_result.known_for_titles),
    )


def build_options(search_results: Iterable[SearchResult]) -> list[Option]:
    if not search_results:
        return [(None, "Search Again")]

    return [
        (search_result, result_to_html_string(search_result)) for search_result in search_results
    ]
