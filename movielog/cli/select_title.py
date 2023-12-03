import html
from typing import Iterable, Optional, Tuple

from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.shortcuts import confirm

from movielog.cli import ask, radio_list, title_searcher

SearchResult = title_searcher.SearchResult
Option = Tuple[Optional[SearchResult], AnyFormattedText]


def prompt(prompt_text: str = "Title: ") -> Optional[SearchResult]:
    while True:
        query = ask.prompt(prompt_text, rprompt="Use ^ and $ to anchor")

        if query is None:
            return None

        search_results = title_searcher.search(query)
        options = build_options(search_results)

        selected_title = radio_list.prompt(
            title='Results for "<cyan>{0}</cyan>":'.format(query),
            options=options,
        )

        if selected_title is None:
            continue

        if confirm(("{0}?".format(result_to_html_string(selected_title)))):
            return selected_title


def result_to_html_string(search_result: SearchResult) -> str:
    return "<cyan>{0}</cyan> ({1})".format(
        html.escape(search_result.full_title),
        ", ".join(
            html.escape(principal) for principal in search_result.principal_cast_names
        ),
    )


def build_options(search_results: Iterable[SearchResult]) -> list[Option]:
    if not search_results:
        return [(None, "Search Again")]

    return [
        (search_result, result_to_html_string(search_result))
        for search_result in search_results
    ]
