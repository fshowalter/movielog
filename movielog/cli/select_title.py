import html
from collections.abc import Iterable
from typing import cast

from prompt_toolkit.formatted_text import HTML, AnyFormattedText
from prompt_toolkit.shortcuts import confirm

from movielog.cli import ask, radio_list, title_searcher

SearchResult = title_searcher.SearchResult
Option = tuple[SearchResult | None, AnyFormattedText]


def prompt(token: str, prompt_text: str = "IMDb ID: ") -> SearchResult | None:
    while True:
        query = ask.prompt(prompt_text)

        if query is None:
            return None

        search_results = title_searcher.search(token, query)
        options = build_options(search_results)

        selected_title = radio_list.prompt(
            title=f'Results for "<cyan>{query}</cyan>":',
            options=options,
        )

        if selected_title is None:
            continue

        if confirm_selected_title(selected_title):
            return selected_title


def confirm_selected_title(selected_title: SearchResult) -> bool:
    prompt_text = HTML(f"{result_to_html_string(selected_title)}?")

    return confirm(cast(str, prompt_text))


def result_to_html_string(search_result: SearchResult) -> str:
    return "<cyan>{}</cyan> ({})".format(
        html.escape(search_result.full_title),
        ", ".join(html.escape(principal) for principal in search_result.principal_cast_names),
    )


def build_options(search_results: Iterable[SearchResult]) -> list[Option]:
    if not search_results:
        return [(None, "Search Again")]

    return [
        (search_result, result_to_html_string(search_result)) for search_result in search_results
    ]
