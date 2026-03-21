from collections import defaultdict
from typing import Literal, TypedDict

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils.logging import logger

_CreditType = Literal["director", "performer", "writer"]


class _JsonCastAndCrewTitle(TypedDict):
    creditedAs: list[_CreditType]
    genres: list[str]
    imdbId: str
    releaseDate: str
    releaseYear: str
    reviewSlug: str | None
    sortTitle: str
    title: str
    watchlistDirectorNames: list[str]
    watchlistPerformerNames: list[str]
    watchlistWriterNames: list[str]
    watchlistCollectionNames: list[str]


_CreditedTitles = dict[str, set[_CreditType]]


class _CastAndCrewMember(TypedDict):
    slug: str
    name: str
    titles: list[_JsonCastAndCrewTitle]
    review_count: int
    total_count: int
    credited_titles: _CreditedTitles


class _JsonCastAndCrewMember(TypedDict):
    name: str
    slug: str
    reviewCount: int
    description: str
    titles: list[_JsonCastAndCrewTitle]
    creditedAs: list[_CreditType]


_CastAndCrewByImdbId = dict[frozenset[str], _CastAndCrewMember]


def _intialize_cast_and_crew_by_imdb_id(
    repository_data: RepositoryData,
) -> _CastAndCrewByImdbId:
    cast_and_crew_by_imdb_id: _CastAndCrewByImdbId = {}

    for member in repository_data.cast_and_crew.values():
        cast_and_crew_by_imdb_id[member.imdb_id] = _CastAndCrewMember(
            name=member.name,
            slug=member.slug,
            titles=[],
            review_count=0,
            total_count=0,
            credited_titles=defaultdict(set),
        )

    return cast_and_crew_by_imdb_id


def _check_title_for_names(
    title: repository_api.Title,
    cast_and_crew_by_imdb_id: _CastAndCrewByImdbId,
) -> None:
    director_ids = frozenset(director.imdb_id for director in title.directors)

    performer_ids = frozenset(performer.imdb_id for performer in title.performers)

    writer_ids = frozenset(writer.imdb_id for writer in title.writers)

    for name_key, name_value in cast_and_crew_by_imdb_id.items():
        if name_key & writer_ids:
            name_value["credited_titles"][title.imdb_id].add("writer")
        if name_key & director_ids:
            name_value["credited_titles"][title.imdb_id].add("director")
        if name_key & performer_ids:
            name_value["credited_titles"][title.imdb_id].add("performer")


def add_watchlist_credits(
    cast_and_crew_by_imdb_id: _CastAndCrewByImdbId, repository_data: RepositoryData
) -> None:
    for watchlist_person_kind in repository_api.WATCHLIST_PERSON_KINDS:
        for watchlist_person in repository_data.watchlist_people[watchlist_person_kind]:
            for title_id in watchlist_person.title_ids:
                title = repository_data.titles[title_id]
                _check_title_for_names(title, cast_and_crew_by_imdb_id)


def _add_review_credits(
    cast_and_crew_by_imdb_id: _CastAndCrewByImdbId, repository_data: RepositoryData
) -> None:
    for reviewed_title in repository_data.reviewed_titles:
        _check_title_for_names(reviewed_title, cast_and_crew_by_imdb_id)


def _build_json_title(
    title_id: str, credited_as: set[_CreditType], repository_data: RepositoryData
) -> _JsonCastAndCrewTitle:
    title = repository_data.titles[title_id]
    review = repository_data.reviews.get(title_id, None)
    return _JsonCastAndCrewTitle(
        imdbId=title.imdb_id,
        title=title.title,
        sortTitle=title.sort_title,
        releaseYear=title.release_year,
        releaseDate=title.release_date,
        genres=title.genres,
        reviewSlug=review.slug if review else None,
        creditedAs=sorted(credited_as),
        watchlistDirectorNames=[
            name for name in repository_data.watchlist_titles[title_id]["directors"] if not review
        ],
        watchlistPerformerNames=[
            name for name in repository_data.watchlist_titles[title_id]["performers"] if not review
        ],
        watchlistWriterNames=[
            name for name in repository_data.watchlist_titles[title_id]["writers"] if not review
        ],
        watchlistCollectionNames=[
            name for name in repository_data.watchlist_titles[title_id]["collections"] if not review
        ],
    )


def _populate_title_data(
    cast_and_crew_by_imdb_id: _CastAndCrewByImdbId, repository_data: RepositoryData
) -> None:
    for name_value in cast_and_crew_by_imdb_id.values():
        for title_id, credited_as in name_value["credited_titles"].items():
            name_value["titles"].append(_build_json_title(title_id, credited_as, repository_data))

        name_value["titles"].sort(key=lambda title: title["imdbId"])


def _populate_counts(
    cast_and_crew_by_imdb_id: _CastAndCrewByImdbId, repository_data: RepositoryData
) -> None:
    for name_value in cast_and_crew_by_imdb_id.values():
        name_value["review_count"] = len(
            repository_data.reviews.keys() & name_value["credited_titles"].keys()
        )
        name_value["total_count"] = len(name_value["credited_titles"].keys())


def _sort_value_for_credit_count(credit_count_item: tuple[str, int]) -> tuple[int, int]:
    credit_order_map = {
        "writer": 3,
        "director": 2,
        "performer": 1,
    }

    return (credit_count_item[1], credit_order_map[credit_count_item[0]])


def _calculate_credit_counts(name: _CastAndCrewMember) -> dict[_CreditType, int]:
    credited_as_counts: dict[_CreditType, int] = defaultdict(int)

    for title_credited_as in name["credited_titles"].values():
        for credit in title_credited_as:
            credited_as_counts[credit] += 1

    return credited_as_counts


def _determine_credited_as(
    member: _CastAndCrewMember,
) -> list[_CreditType]:
    credited_as_counts = _calculate_credit_counts(member)

    credited_as: list[_CreditType] = []

    sorted_credits = sorted(
        credited_as_counts.items(),
        key=_sort_value_for_credit_count,
        reverse=True,
    )

    for credit_kind, _count in sorted_credits:
        credited_as.append(credit_kind)

    return credited_as


def _build_description(credited_as: list[_CreditType], review_count: int, total_count: int) -> str:
    """Build description following the pattern from the Node.js deck function."""
    # Format the credited_as list - Python doesn't have Intl.ListFormat, so we'll replicate it
    if len(credited_as) == 1:
        credit_string: str = credited_as[0]
    elif len(credited_as) == 2:
        credit_string = f"{credited_as[0]} and {credited_as[1]}"
    else:
        credit_string = ", ".join(credited_as[:-1]) + f", and {credited_as[-1]}"

    # Capitalize first letter
    credit_list = credit_string[0].upper() + credit_string[1:]

    # Calculate watchlist count
    watchlist_count = total_count - review_count
    watchlist_title_count = "" if watchlist_count == 0 else f" and {watchlist_count} watchlist"

    # Determine singular/plural for "title(s)"
    titles = "title" if review_count == 1 and watchlist_count < 2 else "titles"

    return f"{credit_list} with {review_count} reviewed{watchlist_title_count} {titles}."


def _transform_to_final(
    cast_and_crew_member: _CastAndCrewMember,
) -> _JsonCastAndCrewMember:
    credited_as = _determine_credited_as(cast_and_crew_member)

    return _JsonCastAndCrewMember(
        name=cast_and_crew_member["name"],
        slug=cast_and_crew_member["slug"],
        reviewCount=cast_and_crew_member["review_count"],
        titles=cast_and_crew_member["titles"],
        description=_build_description(
            credited_as, cast_and_crew_member["review_count"], cast_and_crew_member["total_count"]
        ),
        creditedAs=credited_as,
    )


def _name_has_reviews(name: _CastAndCrewMember) -> bool:
    return name["review_count"] > 0


def _build_cast_and_crew(
    repository_data: RepositoryData,
) -> list[_JsonCastAndCrewMember]:
    cast_and_crew_by_imdb_id = _intialize_cast_and_crew_by_imdb_id(repository_data)

    add_watchlist_credits(cast_and_crew_by_imdb_id, repository_data)
    _add_review_credits(cast_and_crew_by_imdb_id, repository_data)
    _populate_title_data(cast_and_crew_by_imdb_id, repository_data)
    _populate_counts(cast_and_crew_by_imdb_id, repository_data)

    return [
        _transform_to_final(name_value)
        for (_imdb_id, name_value) in cast_and_crew_by_imdb_id.items()
        if _name_has_reviews(name_value)
    ]


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "cast-and-crew")

    cast_and_crew = _build_cast_and_crew(repository_data=repository_data)

    exporter.serialize_dicts_to_folder(
        sorted(cast_and_crew, key=lambda name: name["slug"]),
        "cast-and-crew",
        filename_key=lambda name: name["slug"],
    )
