from itertools import count
from typing import Callable, Optional, Sequence, TypedDict, TypeVar, Union

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils.logging import logger

JsonViewing = TypedDict(
    "JsonViewing",
    {
        "date": str,
        "venue": Optional[str],
        "medium": Optional[str],
        "mediumNotes": Optional[str],
        "sequence": int,
    },
)

JsonMoreTitle = TypedDict(
    "JsonMoreTitle",
    {
        "imdbId": str,
        "title": str,
        "grade": str,
        "year": str,
        "slug": str,
    },
)

JsonMoreEntity = TypedDict(
    "JsonMoreEntity",
    {"name": str, "slug": str, "titles": list[JsonMoreTitle]},
)


JsonMore = TypedDict(
    "JsonMore",
    {
        "directedBy": list[JsonMoreEntity],
        "withPerformer": list[JsonMoreEntity],
        "writtenBy": list[JsonMoreEntity],
        "reviews": list[JsonMoreTitle],
        "inCollection": list[JsonMoreEntity],
    },
)

JsonReviewedTitle = TypedDict(
    "JsonReviewedTitle",
    {
        "sequence": str,
        "imdbId": str,
        "title": str,
        "year": str,
        "slug": str,
        "grade": str,
        "countries": list[str],
        "genres": list[str],
        "sortTitle": str,
        "originalTitle": str,
        "gradeValue": Optional[int],
        "runtimeMinutes": int,
        "directorNames": list[str],
        "principalCastNames": list[str],
        "reviewDate": str,
        "reviewYear": str,
        "viewings": list[JsonViewing],
        "releaseSequence": str,
        "more": JsonMore,
    },
)


def build_json_more_title(
    title: repository_api.Title,
    repository_data: RepositoryData,
) -> JsonMoreTitle:
    review = repository_data.reviews[title.imdb_id]

    assert review

    return JsonMoreTitle(
        title=title.title,
        imdbId=title.imdb_id,
        year=title.year,
        slug=review.slug,
        grade=review.grade,
    )


ListType = TypeVar("ListType")


def slice_list(  # noqa: WPS210
    source_list: list[ListType],
    matcher: Callable[[ListType], bool],
) -> list[ListType]:
    midpoint = next(
        index
        for index, collection_item in zip(count(), source_list)
        if matcher(collection_item)
    )

    start_index = midpoint - 2
    end_index = midpoint + 3

    if start_index >= 0 and end_index < len(source_list):
        return source_list[start_index:end_index]

    if start_index < 0:
        start_index += len(source_list)
    if end_index >= len(source_list):
        end_index -= len(source_list)

    return source_list[start_index:] + source_list[:end_index]


def build_imdb_id_matcher(
    id_to_match: str,
) -> Callable[[Union[repository_api.Title, repository_api.Review]], bool]:
    return lambda item_with_imdb_id: item_with_imdb_id.imdb_id == id_to_match


def build_json_more_for_watchlist_entities(
    review: repository_api.Review,
    watchlist_entities: Sequence[repository_api.WatchlistEntity],
    repository_data: RepositoryData,
) -> list[JsonMoreEntity]:
    more_entries = []
    for watchlist_entity in watchlist_entities:
        reviewed_ids_for_watchlist_entity = (
            repository_data.reviews.keys() & watchlist_entity.title_ids
        )
        if len(reviewed_ids_for_watchlist_entity) < 5:
            continue

        sliced_titles = slice_list(
            source_list=sorted(
                [
                    repository_data.titles[reviewed_id]
                    for reviewed_id in reviewed_ids_for_watchlist_entity
                ],
                key=lambda title: title.release_sequence,
            ),
            matcher=build_imdb_id_matcher(review.imdb_id),
        )

        more_entries.append(
            JsonMoreEntity(
                name=watchlist_entity.name,
                slug=watchlist_entity.slug,
                titles=[
                    build_json_more_title(title=title, repository_data=repository_data)
                    for title in sliced_titles
                    if title.imdb_id != review.imdb_id
                ],
            )
        )

    return more_entries


def build_json_more_reviews(
    review: repository_api.Review,
    repository_data: RepositoryData,
) -> list[JsonMoreTitle]:
    sliced_titles = slice_list(
        source_list=sorted(
            repository_data.reviewed_titles, key=lambda title: title.sort_title
        ),
        matcher=build_imdb_id_matcher(review.imdb_id),
    )

    return [
        build_json_more_title(
            title=sliced_title,
            repository_data=repository_data,
        )
        for sliced_title in sliced_titles
        if sliced_title.imdb_id != review.imdb_id
    ]


def watchlist_people_for_title(
    title: repository_api.Title,
    kind: repository_api.WatchlistPersonKind,
    repository_data: RepositoryData,
) -> list[repository_api.WatchlistPerson]:
    return [
        watchlist_person
        for watchlist_person in repository_data.watchlist_people[kind]
        if title.imdb_id in watchlist_person.title_ids
    ]


def build_json_more(
    title: repository_api.Title,
    review: repository_api.Review,
    repository_data: RepositoryData,
) -> JsonMore:
    return JsonMore(
        directedBy=build_json_more_for_watchlist_entities(
            review=review,
            watchlist_entities=watchlist_people_for_title(
                title=title, kind="directors", repository_data=repository_data
            ),
            repository_data=repository_data,
        ),
        withPerformer=build_json_more_for_watchlist_entities(
            review=review,
            watchlist_entities=watchlist_people_for_title(
                title=title, kind="performers", repository_data=repository_data
            ),
            repository_data=repository_data,
        ),
        writtenBy=build_json_more_for_watchlist_entities(
            review=review,
            watchlist_entities=watchlist_people_for_title(
                title=title, kind="writers", repository_data=repository_data
            ),
            repository_data=repository_data,
        ),
        inCollection=build_json_more_for_watchlist_entities(
            review=review,
            watchlist_entities=[
                collection
                for collection in repository_data.watchlist_collections
                if title.imdb_id in collection.title_ids
            ],
            repository_data=repository_data,
        ),
        reviews=build_json_more_reviews(review=review, repository_data=repository_data),
    )


def build_json_reviewed_title(
    review: repository_api.Review,
    repository_data: RepositoryData,
) -> JsonReviewedTitle:
    title = repository_data.titles[review.imdb_id]
    viewings = sorted(
        [
            viewing
            for viewing in repository_data.viewings
            if viewing.imdb_id == title.imdb_id
        ],
        key=lambda viewing: viewing.sequence,
        reverse=True,
    )

    return JsonReviewedTitle(
        imdbId=title.imdb_id,
        title=title.title,
        year=title.year,
        slug=review.slug,
        grade=review.grade,
        countries=title.countries,
        genres=title.genres,
        sortTitle=title.sort_title,
        originalTitle=title.original_title,
        gradeValue=review.grade_value,
        runtimeMinutes=title.runtime_minutes,
        releaseSequence=title.release_sequence,
        directorNames=[director.name for director in title.directors],
        principalCastNames=[
            performer.name
            for index, performer in enumerate(title.performers)
            if index < 4
        ],
        reviewDate=review.date.isoformat(),
        reviewYear=str(review.date.year),
        sequence="{0}-{1}".format(review.date.isoformat(), viewings[0].sequence),
        viewings=[
            JsonViewing(
                sequence=viewing.sequence,
                medium=viewing.medium,
                mediumNotes=viewing.medium_notes,
                date=viewing.date.isoformat(),
                venue=viewing.venue,
            )
            for viewing in viewings
        ],
        more=build_json_more(
            title=title, review=review, repository_data=repository_data
        ),
    )


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "reviewed-titles")

    json_reviewed_titles = [
        build_json_reviewed_title(review=review, repository_data=repository_data)
        for review in repository_data.reviews.values()
    ]

    exporter.serialize_dicts(
        json_reviewed_titles,
        "reviewed-titles",
    )
