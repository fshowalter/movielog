import html
from typing import List, Optional, Sequence, Tuple

from prompt_toolkit.formatted_text import HTML, AnyFormattedText
from prompt_toolkit.shortcuts import confirm

from movielog.cli import ask, movie_searcher, radio_list

Result = movie_searcher.Result
Option = Tuple[Optional[Result], AnyFormattedText]


def prompt() -> Optional[Result]:
    movie = None

    while movie is None:
        query = ask.prompt("Title: ", rprompt="Use ^ and $ to anchor")
        if query is None:
            break

        search_results = movie_searcher.search_by_title(query)
        options = build_options(search_results)

        movie = radio_list.prompt(
            title=HTML(f'Results for "<cyan>{query}</cyan>":'), options=options,
        )

    if movie:
        if confirm(HTML(f"{result_to_html_string(movie)}?")):
            return movie
    if movie:
        return prompt()
    return None


def result_to_html_string(search_result: Result) -> str:
    return "<cyan>{0} ({1})</cyan> ({2})".format(
        html.escape(search_result.title),
        search_result.year,
        ", ".join(
            html.escape(principal) for principal in search_result.principal_cast_names
        ),
    )


def build_options(search_results: Sequence[Result],) -> Sequence[Option]:
    options: List[Option] = [(None, "Search again")]

    for search_result in search_results:
        options.append((search_result, HTML(result_to_html_string(search_result))))

    return options
