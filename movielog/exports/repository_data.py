from dataclasses import dataclass, field
from datetime import date
from typing import Literal

from movielog.repository import api as repository_api

WatchlistTitlesKey = Literal[repository_api.WatchlistPersonKind, "collections"]

WachlistTitles = dict[str, dict[WatchlistTitlesKey, list[str]]]

WatchlistPeople = dict[repository_api.WatchlistPersonKind, list[repository_api.WatchlistPerson]]


@dataclass
class RepositoryData:
    viewings: list[repository_api.Viewing]
    titles: dict[str, repository_api.Title]
    reviews: dict[str, repository_api.Review]
    reviewed_titles: list[repository_api.Title]
    watchlist_people: WatchlistPeople
    watchlist_titles: WachlistTitles
    collections: list[repository_api.Collection]
    imdb_ratings: repository_api.ImdbRatings
    cast_and_crew: dict[frozenset[str], repository_api.CastAndCrewMember]
    release_sequence_map: dict[str, int] = field(default_factory=dict, init=False)
    review_sequence_map: dict[str, int] = field(default_factory=dict, init=False)
    title_sequence_map: dict[str, int] = field(default_factory=dict, init=False)
    grade_sequence_map: dict[str, int] = field(default_factory=dict, init=False)
    viewing_sequence_map: dict[tuple[str, date, int], int] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        self.release_sequence_map = self._build_release_sequence_map()
        self.review_sequence_map = self._build_review_sequence_map()
        self.grade_sequence_map = self._build_grade_sequence_map()
        self.viewing_sequence_map = self._build_viewing_sequence_map()

    def _build_release_sequence_map(self) -> dict[str, int]:
        """Build a map of title IMDb IDs to release sequence numbers."""
        sequence_map: dict[str, int] = {}

        # Sort titles by release date and IMDb ID for stable ordering
        sorted_titles = sorted(
            self.titles.values(),
            key=lambda title: title.release_sequence,
        )

        for index, title in enumerate(sorted_titles, start=1):
            sequence_map[title.imdb_id] = index

        return sequence_map

    def _build_review_sequence_map(self) -> dict[str, int]:
        """Build a map of title IMDb IDs to review sequence numbers."""
        sequence_map: dict[str, int] = {}

        # Get all reviewed titles with their review dates
        reviewed_with_dates: list[tuple[str, str]] = []

        for imdb_id, review in self.reviews.items():
            # Find the most recent viewing for this title
            viewings = sorted(
                [v for v in self.viewings if v.imdb_id == imdb_id],
                key=lambda v: f"{v.date.isoformat()}-{v.sequence}",
                reverse=True,
            )

            if viewings:
                # Use the sequence of the most recent viewing for stable ordering
                sequence_key = f"{review.date.isoformat()}-{viewings[0].sequence}"
                reviewed_with_dates.append((imdb_id, sequence_key))

        # Sort by the sequence key
        reviewed_with_dates.sort(key=lambda x: x[1])

        for index, (imdb_id, _) in enumerate(reviewed_with_dates, start=1):
            sequence_map[imdb_id] = index

        return sequence_map

    def _build_grade_sequence_map(self) -> dict[str, int]:
        """Build a map of title IMDb IDs to grade sequence numbers."""
        sequence_map: dict[str, int] = {}

        # Get all reviewed titles with their grade values and release sequences
        reviewed_with_grades: list[tuple[str, int, int]] = []

        for imdb_id, review in self.reviews.items():
            title = self.titles.get(imdb_id)
            if title:
                grade_value = review.grade_value
                release_sequence = self.release_sequence_map[imdb_id]
                reviewed_with_grades.append((imdb_id, grade_value, release_sequence))

        # Sort by grade value (descending) and release sequence (ascending)
        reviewed_with_grades.sort(key=lambda x: (-x[1], x[2]))

        for index, (imdb_id, _, _) in enumerate(reviewed_with_grades, start=1):
            sequence_map[imdb_id] = index

        return sequence_map

    def _build_viewing_sequence_map(self) -> dict[tuple[str, date, int], int]:
        """Build a map of (imdb_id, viewing.sequence) tuples to viewing sequence numbers."""
        sequence_map: dict[tuple[str, date, int], int] = {}

        # Sort viewings by date and sequence for stable ordering
        sorted_viewings = sorted(
            self.viewings,
            key=lambda viewing: f"{viewing.date.isoformat()}-{viewing.sequence}",
        )

        for index, viewing in enumerate(sorted_viewings, start=1):
            sequence_map[(viewing.imdb_id, viewing.date, viewing.sequence)] = index

        return sequence_map
