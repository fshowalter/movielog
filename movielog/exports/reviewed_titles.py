from collections import defaultdict
from collections.abc import Callable
from typing import Literal, TypedDict

from movielog.exports import exporter
from movielog.exports.json_reviewed_title import JsonReviewedTitle
from movielog.exports.json_viewed_title import JsonViewedTitle
from movielog.exports.repository_data import RepositoryData
from movielog.exports.utils import calculate_review_sequence, calculate_viewing_sequence
from movielog.repository import api as repository_api
from movielog.utils.logging import logger

_CreditKind = Literal["director", "writer", "performer"]


class _JsonViewing(JsonViewedTitle):
    venueNotes: str | None  # noqa: N815
    mediumNotes: str | None  # noqa: N815


class _JsonMoreCollection(TypedDict):
    name: str
    slug: str
    titles: list[JsonReviewedTitle]


class _JsonMoreCastAndCrewMember(TypedDict):
    name: str
    slug: str
    creditKind: _CreditKind
    titles: list[JsonReviewedTitle]


class _JsonCastAndCrewMember(TypedDict):
    name: str
    slug: str
    creditedAs: list[_CreditKind]


class _JsonCollectionReference(TypedDict):
    name: str
    slug: str


class _JsonFullReviewedTitle(JsonReviewedTitle):
    countries: list[str]
    originalTitle: str | None  # noqa: N815
    runtimeMinutes: int  # noqa: N815
    directorNames: list[str]  # noqa: N815
    principalCastNames: list[str]  # noqa: N815
    writerNames: list[str]  # noqa: N815
    viewings: list[_JsonViewing]
    castAndCrew: list[_JsonCastAndCrewMember]  # noqa: N815
    collections: list[_JsonCollectionReference]
    moreCastAndCrew: list[_JsonMoreCastAndCrewMember]  # noqa: N815
    moreReviews: list[JsonReviewedTitle]  # noqa: N815
    moreCollections: list[_JsonMoreCollection]  # noqa: N815


_TitleIdsByNameId = dict[frozenset[str], set[str]]
_CreditIndex = dict[_CreditKind, _TitleIdsByNameId]
_CollectionIndex = dict[str, set[str]]


def _build_json_more_title(
    title: repository_api.Title,
    repository_data: RepositoryData,
) -> JsonReviewedTitle:
    review = repository_data.reviews[title.imdb_id]

    assert review

    return JsonReviewedTitle(
        title=title.title,
        imdbId=title.imdb_id,
        releaseYear=title.release_year,
        slug=review.slug,
        sortTitle=title.sort_title,
        grade=review.grade,
        gradeValue=review.grade_value,
        reviewDate=review.date.isoformat(),
        reviewSequence=calculate_review_sequence(title.imdb_id, review, repository_data),
        genres=title.genres,
        releaseDate=title.release_date,
    )


def _slice_list[ListType](
    source_list: list[ListType],
    matcher: Callable[[ListType], bool],
) -> list[ListType]:
    """Get a 5-item window around the first matching item, with wraparound.

    Returns 2 items before, the matched item, and 2 items after.
    Raises ValueError if no match is found.
    """
    # Find the index of the first matching item
    try:
        midpoint = next(index for index, item in enumerate(source_list) if matcher(item))
    except StopIteration as e:
        # No matching item found - this indicates inconsistent data
        raise ValueError("No matching item found in list") from e

    # If list has 5 or fewer items, return all of them
    if len(source_list) <= 5:
        return source_list

    # Calculate the slice indices
    result = []
    for offset in range(-2, 3):  # -2, -1, 0, 1, 2
        # Use modulo to handle wraparound
        index = (midpoint + offset) % len(source_list)
        result.append(source_list[index])

    return result


def _build_imdb_id_matcher(
    id_to_match: str,
) -> Callable[[repository_api.Title | repository_api.Review], bool]:
    return lambda item_with_imdb_id: item_with_imdb_id.imdb_id == id_to_match


def _build_json_more_reviews(
    review: repository_api.Review,
    repository_data: RepositoryData,
) -> list[JsonReviewedTitle]:
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
                    key=lambda title: title.imdb_id,
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
                key=lambda title: title.imdb_id,
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
) -> list[_JsonCollectionReference]:
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
            _JsonCollectionReference(
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
) -> _JsonFullReviewedTitle:
    title = repository_data.titles[review.imdb_id]
    viewings = sorted(
        [viewing for viewing in repository_data.viewings if viewing.imdb_id == title.imdb_id],
        key=lambda viewing: f"{viewing.date.isoformat()}-{viewing.sequence}",
        reverse=True,
    )

    original_title = None if title.original_title == title.title else title.original_title

    return _JsonFullReviewedTitle(
        imdbId=title.imdb_id,
        title=title.title,
        sortTitle=title.sort_title,
        releaseYear=title.release_year,
        slug=review.slug,
        grade=review.grade,
        gradeValue=review.grade_value,
        reviewDate=review.date.isoformat(),
        reviewSequence=calculate_review_sequence(title.imdb_id, review, repository_data),
        releaseDate=title.release_date,
        genres=title.genres,
        countries=title.countries,
        originalTitle=original_title,
        runtimeMinutes=title.runtime_minutes,
        directorNames=[director.name for director in title.directors],
        writerNames=list(dict.fromkeys(writer.name for writer in title.writers)),
        principalCastNames=[
            performer.name for index, performer in enumerate(title.performers) if index < 4
        ],
        viewings=[
            _JsonViewing(
                # Base JsonViewedTitle fields
                imdbId=title.imdb_id,
                title=title.title,
                releaseYear=title.release_year,
                sortTitle=title.sort_title,
                releaseDate=title.release_date,
                genres=title.genres,
                # JsonMaybeReviewedTitle fields
                slug=review.slug,
                grade=review.grade,
                gradeValue=review.grade_value,
                reviewDate=review.date.isoformat(),
                reviewSequence=calculate_review_sequence(title.imdb_id, review, repository_data),
                # JsonViewedTitle specific fields
                viewingDate=viewing.date.isoformat(),
                viewingSequence=calculate_viewing_sequence(
                    title.imdb_id, viewing.date, viewing.sequence, repository_data
                ),
                medium=viewing.medium,
                venue=viewing.venue,
                # Additional fields specific to _JsonViewing
                venueNotes=viewing.venue_notes,
                mediumNotes=viewing.medium_notes,
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
