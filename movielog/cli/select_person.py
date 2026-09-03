import html
from collections.abc import Iterable

from prompt_toolkit.formatted_text import HTML, AnyFormattedText
from prompt_toolkit.shortcuts import confirm

from movielog.cli import ask, ask_for_token, person_searcher, radio_list
from movielog.repository import api as repository_api
from movielog.repository import imdb_http

SearchResult = person_searcher.SearchResult
Option = tuple[SearchResult | None, AnyFormattedText]


def _search(
    imdb_session: imdb_http.ImdbSession | None, query: str
) -> tuple[imdb_http.ImdbSession, list[SearchResult]] | None:
    try:
        session = imdb_session or repository_api.create_session(ask_for_token.prompt)
        return session, person_searcher.search_by_name(session, query)
    except imdb_http.TokenPromptCancelledError:
        return None


def prompt(prompt_text: str = "IMDb ID: ") -> SearchResult | None:
    imdb_session: imdb_http.ImdbSession | None = None

    while True:
        query = ask.prompt(prompt_text)

        if query is None:
            return None

        search = _search(imdb_session, query)

        if search is None:
            return None

        imdb_session, search_results = search

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
