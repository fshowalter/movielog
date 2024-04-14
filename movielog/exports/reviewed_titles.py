from collections import defaultdict
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
        "venueNotes": Optional[str],
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

CreditIndex = dict[repository_api.WatchlistPersonKind, dict[frozenset[str], set[str]]]
CollectionIndex = dict[str, set[str]]


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


MoreEntity = TypedDict(
    "MoreEntity",
    {"name": str, "slug": str, "title_ids": set[str]},
)


def build_json_more_for_entities(
    review: repository_api.Review,
    entities: Sequence[MoreEntity],
    repository_data: RepositoryData,
) -> list[JsonMoreEntity]:
    more_entries = []
    for entity in entities:
        if len(entity["title_ids"]) < 5:
            continue

        sliced_titles = slice_list(
            source_list=sorted(
                [repository_data.titles[title_id] for title_id in entity["title_ids"]],
                key=lambda title: title.release_sequence,
            ),
            matcher=build_imdb_id_matcher(review.imdb_id),
        )

        more_entries.append(
            JsonMoreEntity(
                name=entity["name"],
                slug=entity["slug"],
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


def cast_and_crew_for_title(
    title: repository_api.Title,
    kind: repository_api.WatchlistPersonKind,
    credit_index: CreditIndex,
    repository_data: RepositoryData,
) -> list[MoreEntity]:
    cast_and_crew = []

    credit_kind_items = credit_index[kind].items()

    for cast_and_crew_member_id, cast_and_crew_member_titles in credit_kind_items:
        if title.imdb_id not in cast_and_crew_member_titles:
            continue
        cast_and_crew_member = repository_data.cast_and_crew[cast_and_crew_member_id]

        cast_and_crew.append(
            MoreEntity(
                name=cast_and_crew_member.name,
                slug=cast_and_crew_member.slug,
                title_ids=cast_and_crew_member_titles,
            )
        )

    return cast_and_crew


def collections_for_title(
    title: repository_api.Title,
    collection_index: CollectionIndex,
    repository_data: RepositoryData,
) -> list[MoreEntity]:
    collections = []

    for collection_slug, collection_title_ids in collection_index.items():
        if title.imdb_id not in collection_title_ids:
            continue
        collection = next(
            collection
            for collection in repository_data.collections
            if collection.slug == collection_slug
        )

        collections.append(
            MoreEntity(
                name=collection.name,
                slug=collection.slug,
                title_ids=collection_title_ids,
            )
        )

    return collections


def build_json_more(
    title: repository_api.Title,
    review: repository_api.Review,
    repository_data: RepositoryData,
    credit_index: CreditIndex,
    collection_index: CollectionIndex,
) -> JsonMore:
    return JsonMore(
        directedBy=build_json_more_for_entities(
            review=review,
            entities=cast_and_crew_for_title(
                title=title,
                kind="directors",
                repository_data=repository_data,
                credit_index=credit_index,
            ),
            repository_data=repository_data,
        ),
        withPerformer=build_json_more_for_entities(
            review=review,
            entities=cast_and_crew_for_title(
                title=title,
                kind="performers",
                repository_data=repository_data,
                credit_index=credit_index,
            ),
            repository_data=repository_data,
        ),
        writtenBy=build_json_more_for_entities(
            review=review,
            entities=cast_and_crew_for_title(
                title=title,
                kind="writers",
                repository_data=repository_data,
                credit_index=credit_index,
            ),
            repository_data=repository_data,
        ),
        inCollection=build_json_more_for_entities(
            review=review,
            entities=collections_for_title(
                title=title,
                repository_data=repository_data,
                collection_index=collection_index,
            ),
            repository_data=repository_data,
        ),
        reviews=build_json_more_reviews(review=review, repository_data=repository_data),
    )


def build_json_reviewed_title(
    review: repository_api.Review,
    repository_data: RepositoryData,
    credit_index: CreditIndex,
    collection_index: CollectionIndex,
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
                venueNotes=viewing.venue_notes,
            )
            for viewing in viewings
        ],
        more=build_json_more(
            title=title,
            review=review,
            repository_data=repository_data,
            credit_index=credit_index,
            collection_index=collection_index,
        ),
    )


def check_title_for_names(
    title: repository_api.Title,
    credit_index: CreditIndex,
    repository_data: RepositoryData,
) -> None:
    director_ids = frozenset((director.imdb_id for director in title.directors))

    performer_ids = frozenset((performer.imdb_id for performer in title.performers))

    writer_ids = frozenset((writer.imdb_id for writer in title.writers))

    for name_key, _name_value in repository_data.cast_and_crew.items():
        if name_key & writer_ids:
            credit_index["writers"][name_key].add(title.imdb_id)
        if name_key & director_ids:
            credit_index["directors"][name_key].add(title.imdb_id)
        if name_key & performer_ids:
            credit_index["performers"][name_key].add(title.imdb_id)


def add_review_credits(
    credit_index: CreditIndex, repository_data: RepositoryData
) -> None:
    for reviewed_title in repository_data.reviewed_titles:
        check_title_for_names(reviewed_title, credit_index, repository_data)


def build_collection_index(repository_data: RepositoryData) -> CollectionIndex:
    collection_index = defaultdict(set)

    for collection in repository_data.collections:
        reviewed_collection_titles = (
            repository_data.reviews.keys() & collection.title_ids
        )
        if len(reviewed_collection_titles) < 5:
            continue

        collection_index[collection.slug] = reviewed_collection_titles

    return collection_index


def build_credit_index(
    repository_data: RepositoryData,
) -> CreditIndex:
    credit_index: CreditIndex = {
        "directors": defaultdict(set),
        "writers": defaultdict(set),
        "performers": defaultdict(set),
    }

    add_review_credits(credit_index, repository_data)

    return credit_index


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "reviewed-titles")

    credit_index = build_credit_index(repository_data=repository_data)
    collection_index = build_collection_index(repository_data=repository_data)

    json_reviewed_titles = [
        build_json_reviewed_title(
            review=review,
            repository_data=repository_data,
            credit_index=credit_index,
            collection_index=collection_index,
        )
        for review in repository_data.reviews.values()
    ]

    exporter.serialize_dicts(
        json_reviewed_titles,
        "reviewed-titles",
    )
