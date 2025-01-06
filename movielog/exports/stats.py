from collections import defaultdict
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Callable, Iterable, Optional, TypedDict, TypeVar

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils import list_tools
from movielog.utils.logging import logger

CREDIT_TEAMS = MappingProxyType(
    {
        frozenset(("nm0751577", "nm0751648")): "The Russo Brothers",
        frozenset(("nm0001053", "nm0001054")): "The Coen Brothers",
    }
)

EXCLUSIONS = frozenset(("nm0498278", "nm0456158"))

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
        "venueDistribution": list[JsonDistribution],
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
        "venueDistribution": list[JsonDistribution],
    },
)

ListType = TypeVar("ListType")


def _build_json_distributions(
    distribution_items: Iterable[ListType], key: Callable[[ListType], str]
) -> list[JsonDistribution]:
    distribution = list_tools.group_list_by_key(distribution_items, key)

    return [
        JsonDistribution(name=key, count=len(distribution_values))
        for key, distribution_values in distribution.items()
    ]


def _build_json_grade_distributions(
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


NameImdbId = frozenset[str]


def _remove_viewing_for_credit_team_members(
    viewings_by_name: dict[NameImdbId, MostWatchedPersonGroup],
    viewing: repository_api.Viewing,
    team_ids: frozenset[str],
) -> None:
    for team_member_id in team_ids:
        key = frozenset((team_member_id,))
        viewings_by_name[key].viewings = [  # noqa: WPS204
            existing_viewing
            for existing_viewing in viewings_by_name[key].viewings
            if existing_viewing.sequence != viewing.sequence
        ]


def _apply_credit_teams_for_viewing(
    viewings_by_name: dict[NameImdbId, MostWatchedPersonGroup],
    viewing: repository_api.Viewing,
    credit_names: list[repository_api.CreditName],
) -> None:

    for team_ids, team_name in CREDIT_TEAMS.items():
        credit_name_ids = set([name.imdb_id for name in credit_names])

        if team_ids & credit_name_ids:
            viewings_by_name[team_ids].viewings.append(viewing)
            viewings_by_name[team_ids].name = team_name
            _remove_viewing_for_credit_team_members(
                viewings_by_name=viewings_by_name, viewing=viewing, team_ids=team_ids
            )


def _build_most_watched_performers(
    viewings: list[repository_api.Viewing],
    repository_data: RepositoryData,
) -> list[JsonMostWatchedPerson]:
    viewings_by_name: dict[NameImdbId, MostWatchedPersonGroup] = defaultdict(
        MostWatchedPersonGroup
    )

    for viewing in viewings:
        performers = repository_data.titles[viewing.imdb_id].performers  # noqa: WPS204
        for performer in performers:
            key = frozenset((performer.imdb_id,))
            viewings_by_name[key].name = performer.name
            viewings_by_name[key].viewings.append(viewing)

        _apply_credit_teams_for_viewing(
            viewings_by_name=viewings_by_name,
            viewing=viewing,
            credit_names=repository_data.titles[viewing.imdb_id].performers,
        )

    return _build_most_watched_person_list(
        watchlist_kind="performers",
        viewings_by_name=viewings_by_name,
        repository_data=repository_data,
    )


def _build_most_watched_writers(
    viewings: list[repository_api.Viewing],
    repository_data: RepositoryData,
) -> list[JsonMostWatchedPerson]:
    viewings_by_name: dict[NameImdbId, MostWatchedPersonGroup] = defaultdict(
        MostWatchedPersonGroup
    )

    for viewing in viewings:
        for writer in repository_data.titles[viewing.imdb_id].writers:
            if writer.imdb_id in EXCLUSIONS:
                continue
            key = frozenset((writer.imdb_id,))
            viewings_by_name[key].name = writer.name
            if viewing not in viewings_by_name[key].viewings:
                viewings_by_name[key].viewings.append(viewing)

        _apply_credit_teams_for_viewing(
            viewings_by_name=viewings_by_name,
            viewing=viewing,
            credit_names=repository_data.titles[viewing.imdb_id].writers,
        )

    return _build_most_watched_person_list(
        watchlist_kind="writers",
        viewings_by_name=viewings_by_name,
        repository_data=repository_data,
    )


def _build_json_most_watched_person_viewing(
    viewing: repository_api.Viewing, sequence: int, repository_data: RepositoryData
) -> JsonMostWatchedPersonViewing:
    title = repository_data.titles[viewing.imdb_id]
    review = repository_data.reviews.get(title.imdb_id, None)

    return JsonMostWatchedPersonViewing(
        sequence=sequence,
        date=viewing.date.isoformat(),
        slug=review.slug if review else None,
        title=title.title,
        medium=viewing.medium,
        venue=viewing.venue,
        year=title.year,
    )


def _watchlist_person_matches_indexed_imdb_id(
    person_imdb_id: frozenset[str], indexed_imdb_id: NameImdbId
) -> bool:
    return frozenset(person_imdb_id) == indexed_imdb_id


def _build_most_watched_directors(
    viewings: list[repository_api.Viewing],
    repository_data: RepositoryData,
) -> list[JsonMostWatchedPerson]:
    viewings_by_name: dict[NameImdbId, MostWatchedPersonGroup] = defaultdict(
        MostWatchedPersonGroup
    )

    for viewing in viewings:
        for director in repository_data.titles[viewing.imdb_id].directors:
            key = frozenset((director.imdb_id,))
            viewings_by_name[key].name = director.name
            viewings_by_name[key].viewings.append(viewing)

        _apply_credit_teams_for_viewing(
            viewings_by_name=viewings_by_name,
            viewing=viewing,
            credit_names=repository_data.titles[viewing.imdb_id].directors,
        )

    return _build_most_watched_person_list(
        watchlist_kind="directors",
        viewings_by_name=viewings_by_name,
        repository_data=repository_data,
    )


def _build_most_watched_person_list(  # noqa: WPS210
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
                if _watchlist_person_matches_indexed_imdb_id(
                    person_imdb_id=watchlist_person.imdb_id,
                    indexed_imdb_id=indexed_imdb_id,
                )
                and (repository_data.reviews.keys() & watchlist_person.title_ids)
            ),
            None,
        )

        most_watched_person_list.append(
            JsonMostWatchedPerson(
                name=most_watched_person_group.name,
                count=len(most_watched_person_group.viewings),
                slug=watchlist_person.slug if watchlist_person else None,
                viewings=[
                    _build_json_most_watched_person_viewing(
                        viewing=viewing,
                        sequence=index + 1,
                        repository_data=repository_data,
                    )
                    for index, viewing in enumerate(most_watched_person_group.viewings)
                ],
            )
        )

    return sorted(
        most_watched_person_list,
        key=lambda most_watched_person: most_watched_person["count"],
        reverse=True,
    )[:10]


def _build_most_watched_title(
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


def _build_most_watched_titles(
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
            _build_most_watched_title(
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


def _build_grade_distribution(
    reviews: Iterable[repository_api.Review],
) -> list[JsonDistribution]:
    return _build_json_distributions(reviews, lambda review: review.grade)


def _build_venue_distribution(
    viewings: list[repository_api.Viewing],
) -> list[JsonDistribution]:
    return _build_json_distributions(
        [viewing for viewing in viewings if viewing.venue],
        lambda viewing: str(viewing.venue),
    )


def _build_media_distribution(
    viewings: list[repository_api.Viewing],
) -> list[JsonDistribution]:
    return _build_json_distributions(
        [viewing for viewing in viewings if viewing.medium],
        lambda viewing: str(viewing.medium),
    )


def _build_decade_distribution(
    titles: list[repository_api.Title],
) -> list[JsonDistribution]:
    return sorted(
        _build_json_distributions(titles, lambda title: "{0}0s".format(title.year[:3])),
        key=lambda distribution: distribution["name"],
    )


def _build_json_year_stats(
    year: str,
    viewings: list[repository_api.Viewing],
    repository_data: RepositoryData,
) -> JsonYearStats:
    titles = [repository_data.titles[viewing.imdb_id] for viewing in viewings]

    unique_title_ids = set([title.imdb_id for title in titles])

    return JsonYearStats(
        year=year,
        newTitleCount=_new_title_count(
            year=year,
            unique_title_ids_for_year=unique_title_ids,
            repository_data=repository_data,
        ),
        viewingCount=len(viewings),
        titleCount=len(unique_title_ids),
        mediaDistribution=sorted(
            _build_media_distribution(viewings),
            key=lambda distribution: distribution["count"],
            reverse=True,
        )[:10],
        venueDistribution=sorted(
            _build_venue_distribution(viewings),
            key=lambda distribution: distribution["count"],
            reverse=True,
        )[:10],
        decadeDistribution=_build_decade_distribution(titles),
        mostWatchedTitles=_build_most_watched_titles(
            viewings=viewings, repository_data=repository_data
        ),
        mostWatchedDirectors=_build_most_watched_directors(
            viewings=viewings,
            repository_data=repository_data,
        ),
        mostWatchedPerformers=_build_most_watched_performers(
            viewings=viewings,
            repository_data=repository_data,
        ),
        mostWatchedWriters=_build_most_watched_writers(
            viewings=viewings,
            repository_data=repository_data,
        ),
    )


def _build_all_time_json_stats(repository_data: RepositoryData) -> JsonAllTimeStats:
    watchlist_title_ids = _extract_watchlist_title_ids(repository_data=repository_data)

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
        gradeDistribution=_build_json_grade_distributions(
            repository_data.reviews.values()
        ),
        mediaDistribution=sorted(
            _build_media_distribution(repository_data.viewings),
            key=lambda distribution: distribution["count"],
            reverse=True,
        )[:10],
        venueDistribution=sorted(
            _build_venue_distribution(repository_data.viewings),
            key=lambda distribution: distribution["count"],
            reverse=True,
        )[:10],
        decadeDistribution=_build_decade_distribution(titles),
        mostWatchedTitles=_build_most_watched_titles(
            viewings=repository_data.viewings, repository_data=repository_data
        ),
        mostWatchedDirectors=_build_most_watched_directors(
            viewings=repository_data.viewings,
            repository_data=repository_data,
        ),
        mostWatchedPerformers=_build_most_watched_performers(
            viewings=repository_data.viewings,
            repository_data=repository_data,
        ),
        mostWatchedWriters=_build_most_watched_writers(
            viewings=repository_data.viewings,
            repository_data=repository_data,
        ),
    )


def _extract_watchlist_title_ids(repository_data: RepositoryData) -> set[str]:
    watchlist_title_ids = set(
        [
            title_id
            for collection in repository_data.collections
            for title_id in collection.title_ids
        ]
    )

    for person_kind in repository_api.WATCHLIST_PERSON_KINDS:
        for watchlist_person in repository_data.watchlist_people[person_kind]:
            for title_id in watchlist_person.title_ids:
                watchlist_title_ids.add(title_id)

    return watchlist_title_ids


def _new_title_count(
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

    all_time_stats = _build_all_time_json_stats(repository_data=repository_data)

    exporter.serialize_dict(all_time_stats, "all-time-stats")

    viewings_by_year = list_tools.group_list_by_key(
        repository_data.viewings,
        lambda viewing: str(viewing.date.year),
    )

    year_stats = []

    for year, viewings_for_year in viewings_by_year.items():
        if year > "2011":
            year_stats.append(
                _build_json_year_stats(
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
