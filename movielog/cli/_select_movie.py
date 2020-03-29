import html
from typing import Any, Optional, Sequence

from prompt_toolkit.formatted_text import HTML

from movie_db import queries
from movie_db.cli import _ask, _radio_list


def prompt(prompt_text: str) -> Optional[queries.MovieSearchResult]:
    movie = None

    while movie is None:
        query = _ask.prompt(prompt_text, extra_rprompt='Use ^ and $ to anchor')
        if query is None:
            break

        search_results = queries.search_movies_by_title(query)

        movie = _radio_list.prompt(
            title=HTML(f'Results for "<cyan>{query}</cyan>":'),
            options=_build_options(search_results),
        )

    return movie


def format_search_result(search_result: queries.MovieSearchResult, extra_text: str = '') -> Any:
    return HTML('<cyan>{0} ({1})</cyan> ({2}){3}'.format(
        html.escape(search_result.title),
        search_result.year,
        ', '.join(html.escape(principal) for principal in search_result.principals),
        extra_text,
    ))


def _build_options(
    search_results: Sequence[queries.MovieSearchResult],
) -> _radio_list.MovieSearchOptions:
    options = _radio_list.MovieSearchOptions([
        (None, 'Search again'),
    ])

    for search_result in search_results:
        options.append((search_result, format_search_result(search_result)))

    return options
