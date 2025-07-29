from collections import defaultdict
from typing import Literal, TypedDict

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils.logging import logger

CreditType = Literal["director", "performer", "writer"]


class JsonTitle(TypedDict):
    imdbId: str
    title: str
    year: str
    sortTitle: str
    slug: str | None
    grade: str | None
    gradeValue: int | None
    releaseSequence: str
    reviewSequence: str | None
    reviewDate: str | None
    creditedAs: list[CreditType]
    watchlistDirectorNames: list[str]
    watchlistPerformerNames: list[str]
    watchlistWriterNames: list[str]
    collectionNames: list[str]


CreditedTitles = dict[str, set[CreditType]]


class CastAndCrewMember(TypedDict):
    slug: str
    name: str
    titles: list[JsonTitle]
    review_count: int
    total_count: int
    credited_titles: CreditedTitles


class JsonCastAndCrewMember(TypedDict):
    slug: str
    name: str
    titles: list[JsonTitle]
    reviewCount: int
    totalCount: int
    creditedAs: list[CreditType]


CastAndCrewByImdbId = dict[frozenset[str], CastAndCrewMember]


def intialize_cast_and_crew_by_imdb_id(
    repository_data: RepositoryData,
) -> CastAndCrewByImdbId:
    cast_and_crew_by_imdb_id: CastAndCrewByImdbId = {}

    for member in repository_data.cast_and_crew.values():
        cast_and_crew_by_imdb_id[member.imdb_id] = CastAndCrewMember(
            name=member.name,
            slug=member.slug,
            titles=[],
            review_count=0,
            total_count=0,
            credited_titles=defaultdict(set),
        )

    return cast_and_crew_by_imdb_id


def check_title_for_names(
    title: repository_api.Title,
    cast_and_crew_by_imdb_id: CastAndCrewByImdbId,
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
    cast_and_crew_by_imdb_id: CastAndCrewByImdbId, repository_data: RepositoryData
) -> None:
    for watchlist_person_kind in repository_api.WATCHLIST_PERSON_KINDS:
        for watchlist_person in repository_data.watchlist_people[watchlist_person_kind]:
            for title_id in watchlist_person.title_ids:
                title = repository_data.titles[title_id]
                check_title_for_names(title, cast_and_crew_by_imdb_id)


def add_review_credits(
    cast_and_crew_by_imdb_id: CastAndCrewByImdbId, repository_data: RepositoryData
) -> None:
    for reviewed_title in repository_data.reviewed_titles:
        check_title_for_names(reviewed_title, cast_and_crew_by_imdb_id)


def build_json_title(
    title_id: str, credited_as: set[CreditType], repository_data: RepositoryData
) -> JsonTitle:
    title = repository_data.titles[title_id]
    review = repository_data.reviews.get(title_id, None)
    viewings = sorted(
        (viewing for viewing in repository_data.viewings if viewing.imdb_id == title_id),
        key=lambda title_viewing: title_viewing.sequence,
    )

    return JsonTitle(
        creditedAs=sorted(credited_as),
        imdbId=title.imdb_id,
        title=title.title,
        year=title.year,
        slug=review.slug if review else None,
        grade=review.grade if review else None,
        sortTitle=title.sort_title,
        gradeValue=review.grade_value if review else None,
        releaseSequence=title.release_sequence,
        reviewDate=review.date.isoformat() if review else None,
        reviewSequence=(
            f"{review.date.isoformat()}-{viewings[0].sequence}" if viewings and review else None
        ),
        watchlistDirectorNames=[
            name for name in repository_data.watchlist_titles[title_id]["directors"] if not review
        ],
        watchlistPerformerNames=[
            name for name in repository_data.watchlist_titles[title_id]["performers"] if not review
        ],
        watchlistWriterNames=[
            name for name in repository_data.watchlist_titles[title_id]["writers"] if not review
        ],
        collectionNames=[
            name for name in repository_data.watchlist_titles[title_id]["collections"] if not review
        ],
    )


def populate_title_data(
    cast_and_crew_by_imdb_id: CastAndCrewByImdbId, repository_data: RepositoryData
) -> None:
    for name_value in cast_and_crew_by_imdb_id.values():
        for title_id, credited_as in name_value["credited_titles"].items():
            name_value["titles"].append(build_json_title(title_id, credited_as, repository_data))

        name_value["titles"].sort(key=lambda title: title["releaseSequence"])


def populate_counts(
    cast_and_crew_by_imdb_id: CastAndCrewByImdbId, repository_data: RepositoryData
) -> None:
    for name_value in cast_and_crew_by_imdb_id.values():
        name_value["review_count"] = len(
            repository_data.reviews.keys() & name_value["credited_titles"].keys()
        )
        name_value["total_count"] = len(name_value["credited_titles"].keys())


def sort_value_for_credit_count(credit_count_item: tuple[str, int]) -> tuple[int, int]:
    credit_order_map = {
        "writer": 3,
        "director": 2,
        "performer": 1,
    }

    return (credit_count_item[1], credit_order_map[credit_count_item[0]])


def calculate_credit_counts(name: CastAndCrewMember) -> dict[CreditType, int]:
    credited_as_counts: dict[CreditType, int] = defaultdict(int)

    for title_credited_as in name["credited_titles"].values():
        for credit in title_credited_as:
            credited_as_counts[credit] += 1

    return credited_as_counts


def determine_credited_as(
    name: CastAndCrewMember,
) -> list[CreditType]:
    credited_as_counts = calculate_credit_counts(name)

    credited_as: list[CreditType] = []

    sorted_credits = sorted(
        credited_as_counts.items(),
        key=sort_value_for_credit_count,
        reverse=True,
    )

    for credit_kind, _count in sorted_credits:
        credited_as.append(credit_kind)

    return credited_as


def transform_to_final(
    cast_and_crew_member: CastAndCrewMember,
) -> JsonCastAndCrewMember:
    return JsonCastAndCrewMember(
        name=cast_and_crew_member["name"],
        slug=cast_and_crew_member["slug"],
        titles=cast_and_crew_member["titles"],
        reviewCount=cast_and_crew_member["review_count"],
        totalCount=cast_and_crew_member["total_count"],
        creditedAs=determine_credited_as(cast_and_crew_member),
    )


def name_has_reviews(name: CastAndCrewMember) -> bool:
    return name["review_count"] > 0


def build_cast_and_crew(
    repository_data: RepositoryData,
) -> list[JsonCastAndCrewMember]:
    cast_and_crew_by_imdb_id = intialize_cast_and_crew_by_imdb_id(repository_data)

    add_watchlist_credits(cast_and_crew_by_imdb_id, repository_data)
    add_review_credits(cast_and_crew_by_imdb_id, repository_data)
    populate_title_data(cast_and_crew_by_imdb_id, repository_data)
    populate_counts(cast_and_crew_by_imdb_id, repository_data)

    return [
        transform_to_final(name_value)
        for (_imdb_id, name_value) in cast_and_crew_by_imdb_id.items()
        if name_has_reviews(name_value)
    ]


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "cast-and-crew")

    cast_and_crew = build_cast_and_crew(repository_data=repository_data)

    exporter.serialize_dicts_to_folder(
        sorted(cast_and_crew, key=lambda name: name["slug"]),
        "cast-and-crew",
        filename_key=lambda name: name["slug"],
    )
