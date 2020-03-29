import html
from typing import Optional, Sequence

from prompt_toolkit.formatted_text import HTML

from movie_db import queries, watchlist
from movie_db.cli import _ask, _radio_list


def prompt() -> None:
    collection = _radio_list.prompt(
        title=HTML('Add to Collection:'),
        options=_build_add_to_collection_options(),
    )

    if collection:
        movie = _select_movie_for_collection(collection)
        if movie:
            collection.add_title(imdb_id=movie.imdb_id, title=movie.title, year=movie.year)
            collection.save()
        prompt()


def _build_add_to_collection_options() -> _radio_list.CollectionOptions:
    options = _radio_list.CollectionOptions([
        (None, 'Go back'),
    ])

    for collection in watchlist.Collection.unfrozen_items():
        option = HTML(f'<cyan>{collection.name}</cyan>')
        options.append((collection, option))

    return options


def _prompt_for_new_title(collection: watchlist.Collection) -> Optional[str]:
    formatted_titles = []
    for title in collection.titles:
        formatted_titles.append(
            f'\u00B7 {html.escape(title.title)} ({title.year}) \n',
        )

    prompt_text = HTML(
        '<cyan>{0}</cyan> titles:\n{1}\nNew Title: '.format(
            len(formatted_titles),
            ''.join(formatted_titles),
        ),
    )
    return _ask.prompt(prompt_text)


def _select_movie_for_collection(
    collection: watchlist.Collection,
) -> Optional[queries.MovieSearchResult]:
    movie = None

    while movie is None:
        query = _prompt_for_new_title(collection)
        if query is None:
            break

        search_results = queries.search_movies_by_title(query)

        movie = _radio_list.prompt(
            title=HTML(f'Results for "<cyan>{query}</cyan>":'),
            options=build_options_for_select_movie_for_collection(search_results),
        )

    return movie


def build_options_for_select_movie_for_collection(
    search_results: Sequence[queries.MovieSearchResult],
) -> _radio_list.MovieSearchOptions:
    options = _radio_list.MovieSearchOptions([
        (None, 'Search again'),
    ])

    for search_result in search_results:
        option = HTML('<cyan>{0} ({1})</cyan> ({2})'.format(
            html.escape(search_result.title),
            search_result.year,
            ', '.join(html.escape(principal) for principal in search_result.principals),
        ))
        options.append((search_result, option))

    return options
