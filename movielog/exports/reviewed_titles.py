from typing import Callable, Optional, TypedDict, TypeVar, Union

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
        "imdbId": str,
        "title": str,
        "year": str,
        "slug": str,
        "grade": str,
        "countries": list[str],
        "genres": list[str],
        "releaseDate": str,
        "sortTitle": str,
        "originalTitle": str,
        "gradeValue": Optional[int],
        "runtimeMinutes": int,
        "directorNames": list[str],
        "principalCastNames": list[str],
        "reviewDate": str,
        "reviewYear": str,
        "viewings": list[JsonViewing],
        "more": JsonMore,
    },
)


def build_json_more_title(
    title: repository_api.Title,
    repository_data: RepositoryData,
) -> JsonMoreTitle:
    review = title.review(repository_data.reviews)

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
    source_list: list[ListType], matcher: Callable[[ListType], bool]
) -> list[ListType]:
    midpoint = next(
        index
        for index, collection_item in enumerate(source_list)
        if matcher(collection_item)
    )

    collection_length = len(source_list)

    start_index = midpoint - 2
    end_index = midpoint + 3

    if start_index >= 0 and end_index < collection_length:
        return source_list[start_index:end_index]

    if start_index < 0:
        start_index += collection_length
    if end_index > collection_length:
        end_index -= collection_length

    return source_list[start_index:] + source_list[:end_index]


def build_imdb_id_matcher(
    id_to_match: str,
) -> Callable[[Union[repository_api.Title, repository_api.Review]], bool]:
    return lambda item_with_imdb_id: item_with_imdb_id.imdb_id == id_to_match


def build_json_more_entities(
    title: repository_api.Title,
    review: repository_api.Review,
    key: repository_api.WatchlistEntityKind,
    repository_data: RepositoryData,
) -> list[JsonMoreEntity]:
    watchlist_entities = title.watchlist_entities(key, repository_data.watchlist[key])

    more_entries = []
    for watchlist_entity in watchlist_entities:
        reviewed_ids = repository_data.review_ids.intersection(
            watchlist_entity.title_ids
        )
        if len(reviewed_ids) < 5:
            continue

        sliced_titles = slice_list(
            source_list=sorted(
                [
                    title
                    for title in repository_data.titles
                    if title.imdb_id in reviewed_ids
                ],
                key=lambda title: title.release_date,
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
    sliced_reviews = slice_list(
        source_list=repository_data.reviews,
        matcher=build_imdb_id_matcher(review.imdb_id),
    )

    return [
        build_json_more_title(
            title=sliced_review.title(repository_data.titles),
            repository_data=repository_data,
        )
        for sliced_review in sliced_reviews
        if sliced_review.imdb_id != review.imdb_id
    ]


def build_json_more(
    title: repository_api.Title,
    review: repository_api.Review,
    repository_data: RepositoryData,
) -> JsonMore:
    return JsonMore(
        directedBy=build_json_more_entities(
            title=title,
            review=review,
            key="directors",
            repository_data=repository_data,
        ),
        withPerformer=build_json_more_entities(
            title=title,
            review=review,
            key="performers",
            repository_data=repository_data,
        ),
        writtenBy=build_json_more_entities(
            title=title,
            review=review,
            key="writers",
            repository_data=repository_data,
        ),
        inCollection=build_json_more_entities(
            title=title,
            review=review,
            key="collections",
            repository_data=repository_data,
        ),
        reviews=build_json_more_reviews(review=review, repository_data=repository_data),
    )


def build_json_reviewed_title(
    review: repository_api.Review,
    repository_data: RepositoryData,
) -> JsonReviewedTitle:
    title = review.title(repository_data.titles)

    return JsonReviewedTitle(
        imdbId=title.imdb_id,
        title=title.title,
        year=title.year,
        slug=review.slug,
        grade=review.grade,
        countries=title.countries,
        genres=title.genres,
        releaseDate=title.release_date.isoformat(),
        sortTitle=title.sort_title,
        originalTitle=title.original_title,
        gradeValue=review.grade_value,
        runtimeMinutes=title.runtime_minutes,
        directorNames=title.director_names,
        principalCastNames=title.principal_cast_names,
        reviewDate=review.date.isoformat(),
        reviewYear=str(review.date.year),
        viewings=[
            JsonViewing(
                sequence=viewing.sequence,
                medium=viewing.medium,
                mediumNotes=viewing.medium_notes,
                date=viewing.date.isoformat(),
                venue=viewing.venue,
            )
            for viewing in title.viewings(repository_data.viewings)
        ],
        more=build_json_more(
            title=title, review=review, repository_data=repository_data
        ),
    )


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "reviewed-titles")

    json_reviewed_titles = [
        build_json_reviewed_title(review=review, repository_data=repository_data)
        for review in repository_data.reviews
    ]

    exporter.serialize_dicts_to_folder(
        json_reviewed_titles,
        "reviewed-titles",
        filename_key=lambda reviewed_title: reviewed_title["imdbId"],
    )
