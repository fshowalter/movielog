from collections import defaultdict
from typing import Callable, Optional, TypedDict, TypeVar

from movielog.exports import exporter, list_tools
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils.logging import logger

JsonMostWatchedPersonViewing = TypedDict(
    "JsonMostWatchedPersonViewing",
    {
        "sequence": int,
        "date": str,
        "medium": Optional[str],
        "title": str,
        "year": str,
        "venue": Optional[str],
        "slug": Optional[str],
    },
)


JsonMostWatchedPerson = TypedDict(
    "JsonMostWatchedPerson",
    {
        "name": str,
        "count": int,
        "slug": Optional[str],
        "viewings": list[JsonMostWatchedPersonViewing],
    },
)

JsonMostWatchedTitle = TypedDict(
    "JsonMostWatchedTitle",
    {
        "imdbId": str,
        "title": str,
        "year": str,
        "count": int,
        "slug": Optional[str],
    },
)

JsonDistribution = TypedDict(
    "JsonDistribution",
    {
        "name": str,
        "count": int,
    },
)

JsonGradeDistribution = TypedDict(
    "JsonGradeDistribution",
    {"name": str, "count": int, "sortValue": int},
)


JsonStats = TypedDict(
    "JsonStats",
    {
        "span": str,
        "viewingCount": int,
        "titleCount": int,
        "newTitleCount": int,
        "reviewCount": int,
        "watchlistTitlesReviewedCount": int,
        "gradeDistribution": list[JsonGradeDistribution],
        "decadeDistribution": list[JsonDistribution],
        "mediaDistribution": list[JsonDistribution],
        "mostWatchedTitles": list[JsonMostWatchedTitle],
        "mostWatchedDirectors": list[JsonMostWatchedPerson],
        "mostWatchedWriters": list[JsonMostWatchedPerson],
        "mostWatchedPerformers": list[JsonMostWatchedPerson],
    },
)

ListType = TypeVar("ListType")


def build_json_distributions(
    distribution_items: list[ListType], key: Callable[[ListType], str]
) -> list[JsonDistribution]:
    distribution = list_tools.group_list_by_key(distribution_items, key)

    return [
        JsonDistribution(name=key, count=len(distribution_values))
        for key, distribution_values in distribution.items()
    ]


def build_json_grade_distributions(
    reviews: list[repository_api.Review],
) -> list[JsonGradeDistribution]:
    distribution = defaultdict(list)

    for review in reviews:
        distribution[(review.grade, review.grade_value or 0)].append(review)

    return sorted(
        [
            JsonGradeDistribution(name=grade, count=len(reviews), sortValue=grade_value)
            for (grade, grade_value), reviews in distribution.items()
        ],
        key=lambda distribution: distribution["sortValue"],
        reverse=True,
    )


def group_viewings_by_director(
    viewings: list[repository_api.Viewing], repository_data: RepositoryData
) -> dict[tuple[str, str], list[repository_api.Viewing]]:
    viewings_by_director: dict[
        tuple[str, str], list[repository_api.Viewing]
    ] = defaultdict(list)

    for viewing in viewings:
        for director in viewing.title(repository_data.titles).directors:
            viewings_by_director[(director.imdb_id, director.name)].append(viewing)

    return viewings_by_director


def build_json_most_watched_person_viewing(
    viewing: repository_api.Viewing, repository_data: RepositoryData
) -> JsonMostWatchedPersonViewing:
    title = viewing.title(repository_data.titles)
    review = title.review(repository_data.reviews)

    return JsonMostWatchedPersonViewing(
        sequence=viewing.sequence,
        date=viewing.date.isoformat(),
        slug=review.slug if review else None,
        title=title.title,
        medium=viewing.medium,
        venue=viewing.venue,
        year=title.year,
    )


def build_most_watched_directors(
    viewings: list[repository_api.Viewing], repository_data: RepositoryData
) -> list[JsonMostWatchedPerson]:
    viewings_by_director = group_viewings_by_director(
        viewings=viewings, repository_data=repository_data
    )

    most_watched_directors = []

    for (
        _imdb_id,
        director_name,
    ), viewings_for_director in viewings_by_director.items():
        if len(viewings_for_director) < 2:
            continue

        watchlist_director = next(
            (
                watchlist_director
                for watchlist_director in repository_data.watchlist["directors"]
            ),
            None,
        )

        most_watched_directors.append(
            JsonMostWatchedPerson(
                name=director_name,
                count=len(viewings_for_director),
                slug=watchlist_director.slug if watchlist_director else None,
                viewings=[
                    build_json_most_watched_person_viewing(
                        viewing=viewing, repository_data=repository_data
                    )
                    for viewing in viewings_for_director
                ],
            )
        )

    return sorted(
        most_watched_directors,
        key=lambda most_watched_director: most_watched_director["count"],
        reverse=True,
    )[:10]


def build_most_watched_title(
    imdb_id: str, count: int, repository_data: RepositoryData
) -> JsonMostWatchedTitle:
    title = next(title for title in repository_data.titles if title.imdb_id == imdb_id)

    review = title.review(repository_data.reviews)

    return JsonMostWatchedTitle(
        title=title.title,
        imdbId=title.imdb_id,
        year=title.year,
        count=count,
        slug=review.slug if review else None,
    )


def build_most_watched_titles(
    viewings: list[repository_api.Viewing], repository_data: RepositoryData
) -> list[JsonMostWatchedTitle]:
    viewings_by_title = list_tools.group_list_by_key(
        viewings, key=lambda viewing: viewing.imdb_id
    )

    most_watched_titles = []

    for imdb_id, viewings_for_title in viewings_by_title.items():
        if len(viewings_for_title) < 2:
            continue

        most_watched_titles.append(
            build_most_watched_title(
                imdb_id=imdb_id,
                count=len(viewings_for_title),
                repository_data=repository_data,
            )
        )

    return sorted(
        most_watched_titles,
        key=lambda most_watched_title: most_watched_title["count"],
        reverse=True,
    )[:10]


def build_grade_distribution(
    reviews: list[repository_api.Review],
) -> list[JsonDistribution]:
    return build_json_distributions(reviews, lambda review: review.grade)


def build_media_distribution(
    viewings: list[repository_api.Viewing],
) -> list[JsonDistribution]:
    return build_json_distributions(
        [viewing for viewing in viewings if viewing.medium],
        lambda viewing: str(viewing.medium),
    )


def build_decade_distribution(
    titles: list[repository_api.Title],
) -> list[JsonDistribution]:
    return build_json_distributions(
        titles, lambda title: "{0}0s".format(str(title.year)[:3])
    )


def build_json_stats(
    span: str,
    viewings: list[repository_api.Viewing],
    reviews: list[repository_api.Review],
    most_watched_titles: list[JsonMostWatchedTitle],
    repository_data: RepositoryData,
    older_title_ids: set[str],
) -> JsonStats:
    titles = [viewing.title(repository_data.titles) for viewing in viewings]
    unique_title_ids = set([title.imdb_id for title in titles])

    return JsonStats(
        span=span,
        viewingCount=len(viewings),
        titleCount=len(unique_title_ids),
        reviewCount=len(reviews),
        newTitleCount=len(unique_title_ids.difference(older_title_ids)),
        watchlistTitlesReviewedCount=0,
        gradeDistribution=build_json_grade_distributions(reviews),
        mediaDistribution=sorted(
            build_media_distribution(viewings),
            key=lambda distribution: distribution["count"],
            reverse=True,
        )[:10],
        decadeDistribution=build_decade_distribution(titles),
        mostWatchedTitles=most_watched_titles,
        mostWatchedDirectors=build_most_watched_directors(
            viewings=viewings, repository_data=repository_data
        ),
        mostWatchedPerformers=[],
        mostWatchedWriters=[],
    )


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "stats")

    json_reading_stats = [
        build_json_stats(
            span="all-time",
            reviews=repository_data.reviews,
            viewings=repository_data.viewings,
            older_title_ids=set(),
            most_watched_titles=build_most_watched_titles(
                viewings=repository_data.viewings, repository_data=repository_data
            ),
            repository_data=repository_data,
        )
    ]

    # reviews_by_year = list_tools.group_list_by_key(
    #     repository_data.reviews, lambda review: str(review.date.year)
    # )

    # readings_by_year = list_tools.group_list_by_key(
    #     repository_data.readings,
    #     lambda reading: str(date_finished_or_abandoned(reading).year),
    # )

    # for year, readings_for_year in readings_by_year.items():
    #     json_reading_stats.append(
    #         build_json_reading_stats(
    #             span=year,
    #             reviews=reviews_by_year[year],
    #             readings=readings_for_year,
    #             most_read_authors=build_most_read_authors(
    #                 readings=readings_for_year, repository_data=repository_data
    #             ),
    #             repository_data=repository_data,
    #         )
    #     )

    exporter.serialize_dicts_to_folder(
        json_reading_stats,
        "stats",
        filename_key=lambda stats: stats["span"],
    )
