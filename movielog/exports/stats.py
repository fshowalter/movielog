from collections import defaultdict
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Callable, Iterable, Optional, TypedDict, TypeVar, Union

from movielog.exports import exporter, list_tools
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils.logging import logger

CREDIT_TEAMS = MappingProxyType(
    {
        ("nm0751577", "nm0751648"): "The Russo Brothers",
        ("nm0001053", "nm0001054"): "The Coen Brothers",
    }
)

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


JsonAllTimeStats = TypedDict(
    "JsonAllTimeStats",
    {
        "viewingCount": int,
        "titleCount": int,
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

JsonYearStats = TypedDict(
    "JsonYearStats",
    {
        "year": str,
        "viewingCount": int,
        "titleCount": int,
        "newTitleCount": int,
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
    distribution_items: Iterable[ListType], key: Callable[[ListType], str]
) -> list[JsonDistribution]:
    distribution = list_tools.group_list_by_key(distribution_items, key)

    return [
        JsonDistribution(name=key, count=len(distribution_values))
        for key, distribution_values in distribution.items()
    ]


def build_json_grade_distributions(
    reviews: Iterable[repository_api.Review],
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


@dataclass
class MostWatchedPersonGroup:
    name: str = ""
    viewings: list[repository_api.Viewing] = field(default_factory=list)


NameImdbId = Union[str, tuple[str, ...]]


def group_viewings_by_name(
    viewings: list[repository_api.Viewing],
    names: list[repository_api.Name],
) -> dict[NameImdbId, MostWatchedPersonGroup]:
    viewings_by_name: dict[NameImdbId, MostWatchedPersonGroup] = defaultdict(
        MostWatchedPersonGroup
    )

    for viewing in viewings:
        for name in names:
            viewings_by_name[name.imdb_id].name = name.name
            viewings_by_name[name.imdb_id].viewings.append(viewing)

    apply_credit_teams(viewings_by_name=viewings_by_name)

    return viewings_by_name


def title_ids_for_credit_team(
    viewings_by_name: dict[NameImdbId, MostWatchedPersonGroup],
    credit_team_ids: tuple[str, ...],
) -> set[str]:
    viewings_for_team_members = [
        viewings_by_name[team_id].viewings for team_id in credit_team_ids
    ]

    title_ids_for_team_member_viewing_groups = [
        list(map(lambda viewing: viewing.imdb_id, viewing_group))
        for viewing_group in viewings_for_team_members
    ]

    return set.intersection(*map(set, title_ids_for_team_member_viewing_groups))


def apply_credit_teams(
    viewings_by_name: dict[NameImdbId, MostWatchedPersonGroup],
) -> None:
    for team_ids, team_name in CREDIT_TEAMS.items():
        team_title_ids = title_ids_for_credit_team(
            viewings_by_name=viewings_by_name, credit_team_ids=team_ids
        )
        viewings_cache = []
        for team_member_id in team_ids:
            viewings_cache = viewings_by_name[team_member_id].viewings
            viewings_by_name[team_member_id].viewings = [
                viewing_for_person
                for viewing_for_person in viewings_by_name[team_member_id].viewings
                if viewing_for_person.imdb_id not in team_title_ids
            ]

        viewings_by_name[team_ids].name = team_name
        viewings_by_name[team_ids].viewings = [
            team_viewing
            for team_viewing in viewings_cache
            if team_viewing.imdb_id in team_title_ids
        ]


def build_most_watched_performers(
    viewings: list[repository_api.Viewing],
    repository_data: RepositoryData,
) -> list[JsonMostWatchedPerson]:
    viewings_by_name: dict[NameImdbId, MostWatchedPersonGroup] = defaultdict(
        MostWatchedPersonGroup
    )

    for viewing in viewings:
        for performer in repository_data.titles[viewing.imdb_id].performers:
            viewings_by_name[performer.imdb_id].name = performer.name
            viewings_by_name[performer.imdb_id].viewings.append(viewing)

    apply_credit_teams(viewings_by_name=viewings_by_name)

    return build_most_watched_person_list(
        watchlist_kind="performers",
        viewings_by_name=viewings_by_name,
        repository_data=repository_data,
    )


def build_most_watched_writers(
    viewings: list[repository_api.Viewing],
    repository_data: RepositoryData,
) -> list[JsonMostWatchedPerson]:
    viewings_by_name: dict[NameImdbId, MostWatchedPersonGroup] = defaultdict(
        MostWatchedPersonGroup
    )

    for viewing in viewings:
        for writer in repository_data.titles[viewing.imdb_id].writers:
            viewings_by_name[writer.imdb_id].name = writer.name
            viewings_by_name[writer.imdb_id].viewings.append(viewing)

    apply_credit_teams(viewings_by_name=viewings_by_name)

    return build_most_watched_person_list(
        watchlist_kind="writers",
        viewings_by_name=viewings_by_name,
        repository_data=repository_data,
    )


def build_json_most_watched_person_viewing(
    viewing: repository_api.Viewing, repository_data: RepositoryData
) -> JsonMostWatchedPersonViewing:
    title = repository_data.titles[viewing.imdb_id]
    review = repository_data.reviews.get(title.imdb_id, None)

    return JsonMostWatchedPersonViewing(
        sequence=viewing.sequence,
        date=viewing.date.isoformat(),
        slug=review.slug if review else None,
        title=title.title,
        medium=viewing.medium,
        venue=viewing.venue,
        year=title.year,
    )


def watchlist_person_matches_indexed_imdb_id(
    person_imdb_id: Union[str, list[str]], indexed_imdb_id: NameImdbId
) -> bool:
    if isinstance(person_imdb_id, str) and isinstance(indexed_imdb_id, str):
        return person_imdb_id == indexed_imdb_id

    if isinstance(person_imdb_id, list) and isinstance(indexed_imdb_id, tuple):
        return set(person_imdb_id) == set(indexed_imdb_id)

    return False


def build_most_watched_directors(
    viewings: list[repository_api.Viewing],
    repository_data: RepositoryData,
) -> list[JsonMostWatchedPerson]:
    viewings_by_name: dict[NameImdbId, MostWatchedPersonGroup] = defaultdict(
        MostWatchedPersonGroup
    )

    for viewing in viewings:
        for director in repository_data.titles[viewing.imdb_id].directors:
            viewings_by_name[director.imdb_id].name = director.name
            viewings_by_name[director.imdb_id].viewings.append(viewing)

    apply_credit_teams(viewings_by_name=viewings_by_name)

    return build_most_watched_person_list(
        watchlist_kind="directors",
        viewings_by_name=viewings_by_name,
        repository_data=repository_data,
    )


def build_most_watched_person_list(
    watchlist_kind: repository_api.WatchlistPersonKind,
    viewings_by_name: dict[NameImdbId, MostWatchedPersonGroup],
    repository_data: RepositoryData,
) -> list[JsonMostWatchedPerson]:
    most_watched_person_list = []

    for indexed_imdb_id, most_watched_person_group in viewings_by_name.items():
        if len(most_watched_person_group.viewings) < 2:
            continue

        watchlist_person = next(
            (
                watchlist_person
                for watchlist_person in repository_data.watchlist_people[watchlist_kind]
                if watchlist_person_matches_indexed_imdb_id(
                    person_imdb_id=watchlist_person.imdb_id,
                    indexed_imdb_id=indexed_imdb_id,
                )
            ),
            None,
        )

        most_watched_person_list.append(
            JsonMostWatchedPerson(
                name=most_watched_person_group.name,
                count=len(most_watched_person_group.viewings),
                slug=watchlist_person.slug if watchlist_person else None,
                viewings=[
                    build_json_most_watched_person_viewing(
                        viewing=viewing, repository_data=repository_data
                    )
                    for viewing in most_watched_person_group.viewings
                ],
            )
        )

    return sorted(
        most_watched_person_list,
        key=lambda most_watched_person: most_watched_person["count"],
        reverse=True,
    )[:10]


def build_most_watched_title(
    imdb_id: str, count: int, repository_data: RepositoryData
) -> JsonMostWatchedTitle:
    title = repository_data.titles[imdb_id]

    review = repository_data.reviews.get(imdb_id, None)

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
    reviews: Iterable[repository_api.Review],
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
    return sorted(
        build_json_distributions(titles, lambda title: "{0}0s".format(title.year[:3])),
        key=lambda distribution: distribution["name"],
    )


def build_json_year_stats(
    year: str,
    viewings: list[repository_api.Viewing],
    repository_data: RepositoryData,
) -> JsonYearStats:
    titles = [repository_data.titles[viewing.imdb_id] for viewing in viewings]

    unique_title_ids = set([title.imdb_id for title in titles])

    return JsonYearStats(
        year=year,
        newTitleCount=new_title_count(
            year=year,
            unique_title_ids_for_year=unique_title_ids,
            repository_data=repository_data,
        ),
        viewingCount=len(viewings),
        titleCount=len(unique_title_ids),
        mediaDistribution=sorted(
            build_media_distribution(viewings),
            key=lambda distribution: distribution["count"],
            reverse=True,
        )[:10],
        decadeDistribution=build_decade_distribution(titles),
        mostWatchedTitles=build_most_watched_titles(
            viewings=viewings, repository_data=repository_data
        ),
        mostWatchedDirectors=build_most_watched_directors(
            viewings=viewings,
            repository_data=repository_data,
        ),
        mostWatchedPerformers=build_most_watched_performers(
            viewings=viewings,
            repository_data=repository_data,
        ),
        mostWatchedWriters=build_most_watched_directors(
            viewings=viewings,
            repository_data=repository_data,
        ),
    )


def build_all_time_json_stats(repository_data: RepositoryData) -> JsonAllTimeStats:
    watchlist_title_ids = extract_watchlist_title_ids(repository_data=repository_data)

    titles = [
        repository_data.titles[viewing.imdb_id] for viewing in repository_data.viewings
    ]

    unique_title_ids = set([title.imdb_id for title in titles])

    review_ids_from_watchlist = repository_data.reviews.keys() & watchlist_title_ids

    return JsonAllTimeStats(
        viewingCount=len(repository_data.viewings),
        titleCount=len(unique_title_ids),
        reviewCount=len(repository_data.reviews),
        watchlistTitlesReviewedCount=len(review_ids_from_watchlist),
        gradeDistribution=build_json_grade_distributions(
            repository_data.reviews.values()
        ),
        mediaDistribution=sorted(
            build_media_distribution(repository_data.viewings),
            key=lambda distribution: distribution["count"],
            reverse=True,
        )[:10],
        decadeDistribution=build_decade_distribution(titles),
        mostWatchedTitles=build_most_watched_titles(
            viewings=repository_data.viewings, repository_data=repository_data
        ),
        mostWatchedDirectors=build_most_watched_directors(
            viewings=repository_data.viewings,
            repository_data=repository_data,
        ),
        mostWatchedPerformers=build_most_watched_performers(
            viewings=repository_data.viewings,
            repository_data=repository_data,
        ),
        mostWatchedWriters=build_most_watched_directors(
            viewings=repository_data.viewings,
            repository_data=repository_data,
        ),
    )


def extract_watchlist_title_ids(repository_data: RepositoryData) -> set[str]:
    watchlist_title_ids = set(
        [
            title_id
            for collection in repository_data.watchlist_collections
            for title_id in collection.title_ids
        ]
    )

    for person_kind in repository_api.WATCHLIST_PERSON_KINDS:
        for watchlist_person in repository_data.watchlist_people[person_kind]:
            for title_id in watchlist_person.title_ids:
                watchlist_title_ids.add(title_id)

    return watchlist_title_ids


def new_title_count(
    year: str, unique_title_ids_for_year: set[str], repository_data: RepositoryData
) -> int:
    older_title_ids = set(
        [
            viewing.imdb_id
            for viewing in repository_data.viewings
            if str(viewing.date.year) < year
        ]
    )

    return len(unique_title_ids_for_year.difference(older_title_ids))


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "stats")

    all_time_stats = build_all_time_json_stats(repository_data=repository_data)

    exporter.serialize_dicts_to_folder(
        [all_time_stats], "all-time-stats", lambda _dict: "all-time-stats"
    )

    viewings_by_year = list_tools.group_list_by_key(
        repository_data.viewings,
        lambda viewing: str(viewing.date.year),
    )

    year_stats = []

    for year, viewings_for_year in viewings_by_year.items():
        year_stats.append(
            build_json_year_stats(
                year=year,
                viewings=viewings_for_year,
                repository_data=repository_data,
            )
        )

    exporter.serialize_dicts_to_folder(
        year_stats,
        "year-stats",
        filename_key=lambda stats: stats["year"],
    )
