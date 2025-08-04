from collections import defaultdict
from collections.abc import Callable
from itertools import count
from typing import Literal, TypedDict, TypeVar

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils.logging import logger

_CreditKind = Literal["director", "writer", "performer"]


class _JsonViewing(TypedDict):
    date: str
    venue: str | None
    venueNotes: str | None
    medium: str | None
    mediumNotes: str | None
    sequence: int


class _JsonMoreTitle(TypedDict):
    imdbId: str
    title: str
    grade: str
    releaseYear: str
    slug: str
    genres: list[str]


class _JsonMoreCollection(TypedDict):
    name: str
    slug: str
    titles: list[_JsonMoreTitle]


class _JsonMoreCastAndCrewMember(TypedDict):
    name: str
    slug: str
    creditKind: _CreditKind
    titles: list[_JsonMoreTitle]


class _JsonCastAndCrewMember(TypedDict):
    name: str
    slug: str
    creditedAs: list[_CreditKind]


class _JsonCollection(TypedDict):
    name: str
    slug: str


class _JsonReviewedTitle(TypedDict):
    sequence: str
    imdbId: str
    title: str
    releaseYear: str
    slug: str
    grade: str
    countries: list[str]
    genres: list[str]
    sortTitle: str
    originalTitle: str | None
    gradeValue: int | None
    runtimeMinutes: int
    directorNames: list[str]
    principalCastNames: list[str]
    writerNames: list[str]
    reviewDate: str
    reviewYear: str
    viewings: list[_JsonViewing]
    releaseSequence: str
    castAndCrew: list[_JsonCastAndCrewMember]
    collections: list[_JsonCollection]
    moreCastAndCrew: list[_JsonMoreCastAndCrewMember]
    moreReviews: list[_JsonMoreTitle]
    moreCollections: list[_JsonMoreCollection]


_TitleIdsByNameId = dict[frozenset[str], set[str]]
_CreditIndex = dict[_CreditKind, _TitleIdsByNameId]
_CollectionIndex = dict[str, set[str]]


def _build_json_more_title(
    title: repository_api.Title,
    repository_data: RepositoryData,
) -> _JsonMoreTitle:
    review = repository_data.reviews[title.imdb_id]

    assert review

    return _JsonMoreTitle(
        title=title.title,
        imdbId=title.imdb_id,
        releaseYear=title.release_year,
        slug=review.slug,
        grade=review.grade,
        genres=title.genres,
    )


_ListType = TypeVar("_ListType")


def _slice_list(
    source_list: list[_ListType],
    matcher: Callable[[_ListType], bool],
) -> list[_ListType]:
    midpoint = next(
        index for index, collection_item in zip(count(), source_list) if matcher(collection_item)
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


def _build_imdb_id_matcher(
    id_to_match: str,
) -> Callable[[repository_api.Title | repository_api.Review], bool]:
    return lambda item_with_imdb_id: item_with_imdb_id.imdb_id == id_to_match


def _build_json_more_reviews(
    review: repository_api.Review,
    repository_data: RepositoryData,
) -> list[_JsonMoreTitle]:
    sliced_titles = _slice_list(
        source_list=sorted(
            repository_data.reviewed_titles,
            key=lambda title: title.sort_title,
        ),
        matcher=_build_imdb_id_matcher(review.imdb_id),
    )

    return [
        _build_json_more_title(
            title=sliced_title,
            repository_data=repository_data,
        )
        for sliced_title in sliced_titles
        if sliced_title.imdb_id != review.imdb_id
    ]


def _build_json_more_cast_and_crew(
    review: repository_api.Review,
    credit_index: _CreditIndex,
    repository_data: RepositoryData,
) -> list[_JsonMoreCastAndCrewMember]:
    cast_and_crew: dict[frozenset[str], _JsonMoreCastAndCrewMember] = {}

    for credit_kind, indexed_names in credit_index.items():
        for member_id, member_titles in indexed_names.items():
            if review.imdb_id not in member_titles or len(member_titles) < 5:
                continue

            if member_id in cast_and_crew:
                continue

            cast_and_crew_member = repository_data.cast_and_crew[member_id]

            sliced_titles = _slice_list(
                source_list=sorted(
                    [repository_data.titles[title_id] for title_id in member_titles],
                    key=lambda title: title.release_sequence,
                ),
                matcher=_build_imdb_id_matcher(review.imdb_id),
            )

            cast_and_crew[member_id] = _JsonMoreCastAndCrewMember(
                name=cast_and_crew_member.name,
                slug=cast_and_crew_member.slug,
                creditKind=credit_kind,
                titles=[
                    _build_json_more_title(title=title, repository_data=repository_data)
                    for title in sliced_titles
                    if title.imdb_id != review.imdb_id
                ],
            )

    return [cast_and_crew_member for _member_id, cast_and_crew_member in cast_and_crew.items()]


def _build_json_more_collections(
    review: repository_api.Review,
    collection_index: _CollectionIndex,
    repository_data: RepositoryData,
) -> list[_JsonMoreCollection]:
    more_collections = []

    for collection_slug, collection_title_ids in collection_index.items():
        if review.imdb_id not in collection_title_ids or len(collection_title_ids) < 5:
            continue

        sliced_titles = _slice_list(
            source_list=sorted(
                [repository_data.titles[title_id] for title_id in collection_title_ids],
                key=lambda title: title.release_sequence,
            ),
            matcher=_build_imdb_id_matcher(review.imdb_id),
        )

        collection = next(
            collection
            for collection in repository_data.collections
            if collection.slug == collection_slug
        )

        more_collections.append(
            _JsonMoreCollection(
                name=collection.name,
                slug=collection.slug,
                titles=[
                    _build_json_more_title(title=title, repository_data=repository_data)
                    for title in sliced_titles
                    if title.imdb_id != review.imdb_id
                ],
            )
        )

    return more_collections


def _build_json_collections(
    review: repository_api.Review,
    collection_index: _CollectionIndex,
    repository_data: RepositoryData,
) -> list[_JsonCollection]:
    json_collections = []

    for collection_slug, collection_title_ids in collection_index.items():
        if review.imdb_id not in collection_title_ids:
            continue

        collection = next(
            collection
            for collection in repository_data.collections
            if collection.slug == collection_slug
        )

        json_collections.append(
            _JsonCollection(
                name=collection.name,
                slug=collection.slug,
            )
        )

    return json_collections


def _build_json_cast_and_crew(
    review: repository_api.Review,
    repository_data: RepositoryData,
    credit_index: _CreditIndex,
) -> list[_JsonCastAndCrewMember]:
    cast_and_crew: dict[frozenset[str], _JsonCastAndCrewMember] = {}

    for credit_kind, members in credit_index.items():
        for member_id, member_title_ids in members.items():
            if review.imdb_id in member_title_ids:
                existing_member = cast_and_crew.get(member_id)
                if existing_member:
                    existing_member["creditedAs"].append(credit_kind)
                else:
                    member = repository_data.cast_and_crew[member_id]
                    cast_and_crew[member_id] = _JsonCastAndCrewMember(
                        name=member.name, slug=member.slug, creditedAs=[credit_kind]
                    )

    return list(cast_and_crew.values())


def _build_json_reviewed_title(
    review: repository_api.Review,
    repository_data: RepositoryData,
    credit_index: _CreditIndex,
    collection_index: _CollectionIndex,
) -> _JsonReviewedTitle:
    title = repository_data.titles[review.imdb_id]
    viewings = sorted(
        [viewing for viewing in repository_data.viewings if viewing.imdb_id == title.imdb_id],
        key=lambda viewing: f"{viewing.date.isoformat()}-{viewing.sequence}",
        reverse=True,
    )

    original_title = None if title.original_title == title.title else title.original_title

    return _JsonReviewedTitle(
        imdbId=title.imdb_id,
        title=title.title,
        releaseYear=title.release_year,
        slug=review.slug,
        grade=review.grade,
        countries=title.countries,
        genres=title.genres,
        sortTitle=title.sort_title,
        originalTitle=original_title,
        gradeValue=review.grade_value,
        runtimeMinutes=title.runtime_minutes,
        releaseSequence=title.release_sequence,
        directorNames=[director.name for director in title.directors],
        writerNames=list(dict.fromkeys(writer.name for writer in title.writers)),
        principalCastNames=[
            performer.name for index, performer in enumerate(title.performers) if index < 4
        ],
        reviewDate=review.date.isoformat(),
        reviewYear=str(review.date.year),
        sequence="{}-{}".format(review.date.isoformat(), viewings[0].sequence if viewings else ""),
        viewings=[
            _JsonViewing(
                sequence=viewing.sequence,
                medium=viewing.medium,
                mediumNotes=viewing.medium_notes,
                date=viewing.date.isoformat(),
                venue=viewing.venue,
                venueNotes=viewing.venue_notes,
            )
            for viewing in viewings
        ],
        castAndCrew=_build_json_cast_and_crew(
            review=review, repository_data=repository_data, credit_index=credit_index
        ),
        collections=_build_json_collections(
            review=review,
            collection_index=collection_index,
            repository_data=repository_data,
        ),
        moreCastAndCrew=_build_json_more_cast_and_crew(
            review=review, credit_index=credit_index, repository_data=repository_data
        ),
        moreCollections=_build_json_more_collections(
            review=review,
            collection_index=collection_index,
            repository_data=repository_data,
        ),
        moreReviews=_build_json_more_reviews(review=review, repository_data=repository_data),
    )


def _check_title_for_names(
    title: repository_api.Title,
    credit_index: _CreditIndex,
    repository_data: RepositoryData,
) -> None:
    director_ids = frozenset(director.imdb_id for director in title.directors)

    performer_ids = frozenset(performer.imdb_id for performer in title.performers)

    writer_ids = frozenset(writer.imdb_id for writer in title.writers)

    for name_key in repository_data.cast_and_crew:
        if name_key & writer_ids:
            credit_index["writer"][name_key].add(title.imdb_id)
        if name_key & director_ids:
            credit_index["director"][name_key].add(title.imdb_id)
        if name_key & performer_ids:
            credit_index["performer"][name_key].add(title.imdb_id)


def _add_review_credits(credit_index: _CreditIndex, repository_data: RepositoryData) -> None:
    for reviewed_title in repository_data.reviewed_titles:
        _check_title_for_names(reviewed_title, credit_index, repository_data)


def _build_collection_index(repository_data: RepositoryData) -> _CollectionIndex:
    collection_index = defaultdict(set)

    for collection in repository_data.collections:
        reviewed_collection_titles = repository_data.reviews.keys() & collection.title_ids
        collection_index[collection.slug] = reviewed_collection_titles

    return collection_index


def _build_credit_index(
    repository_data: RepositoryData,
) -> _CreditIndex:
    credit_index: _CreditIndex = {
        "director": defaultdict(set),
        "writer": defaultdict(set),
        "performer": defaultdict(set),
    }

    _add_review_credits(credit_index, repository_data)

    return credit_index


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "reviewed-titles")

    credit_index = _build_credit_index(repository_data=repository_data)
    collection_index = _build_collection_index(repository_data=repository_data)

    json_reviewed_titles = [
        _build_json_reviewed_title(
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
