import datetime
from dataclasses import dataclass
from typing import Iterable, Optional, Sequence

from movielog.repository import (
    json_metadata,
    json_titles,
    json_viewings,
    markdown_reviews,
)
from movielog.repository.datasets import api as datasets_api
from movielog.repository.db import api as db_api

RECENT_VIEWING_DAYS = 365


@dataclass
class Title(object):
    imdb_id: str
    title: str
    release_date: datetime.date
    sort_title: str
    year: str
    genres: list[str]
    runtime_minutes: int
    countries: list[str]
    director_names: list[str]
    principal_cast_names: list[str]
    original_title: str

    def review(self, cache: Optional[list["Review"]] = None) -> Optional["Review"]:
        review_iterable = cache or reviews()
        return next(
            (review for review in review_iterable if review.imdb_id == self.imdb_id),
            None,
        )

    def viewings(self, cache: Optional[list["Viewing"]] = None) -> list["Viewing"]:
        viewing_iterable = cache or viewings()
        return [
            viewing for viewing in viewing_iterable if viewing.imdb_id == self.imdb_id
        ]


@dataclass
class Viewing(object):
    imdb_id: str
    sequence: int
    viewing_date: datetime.date
    medium: Optional[str]
    venue: Optional[str]
    medium_notes: Optional[str]

    def title(self, cache: Optional[list[Title]] = None) -> Title:
        title_iterable = cache or titles()
        return next(title for title in title_iterable if title.imdb_id == self.imdb_id)


@dataclass
class Review(object):
    imdb_id: str
    slug: str
    grade: str
    review_content: Optional[str]
    date: datetime.date

    @property
    def grade_value(self) -> Optional[int]:
        if not self.grade:
            return None

        value_modifier = 1

        grade_map = {
            "A": 12,
            "B": 9,
            "C": 6,
            "D": 3,
        }

        grade_value = grade_map.get(self.grade[0], 1)
        modifier = self.grade[-1]

        if modifier == "+":
            grade_value += value_modifier

        if modifier == "-":
            grade_value -= value_modifier

        return grade_value


def hydrate_json_title(json_title: json_titles.JsonTitle) -> Title:
    return Title(
        imdb_id=json_title["imdbId"],
        title=json_title["imdbId"],
        release_date=datetime.date.fromisoformat(json_title["releaseDate"]),
        sort_title=json_title["sortTitle"],
        year=json_title["year"],
        genres=json_title["genres"],
        original_title=json_title["originalTitle"],
        runtime_minutes=json_title["runtimeMinutes"],
        countries=json_title["countries"],
        director_names=[director["name"] for director in json_title["directors"]],
        principal_cast_names=[
            performer["name"]
            for index, performer in enumerate(json_title["performers"])
            if index < 4
        ],
    )


def hydrate_json_viewing(json_viewing: json_viewings.JsonViewing) -> Viewing:
    return Viewing(
        imdb_id=json_viewing["imdbId"],
        sequence=json_viewing["sequence"],
        medium=json_viewing["medium"],
        venue=json_viewing["medium"],
        viewing_date=datetime.date.fromisoformat(json_viewing["date"]),
        medium_notes=json_viewing["mediumNotes"],
    )


def hydrate_markdown_review(markdown_review: markdown_reviews.MarkdownReview) -> Review:
    return Review(
        slug=markdown_review.yaml["slug"],
        date=markdown_review.yaml["date"],
        grade=markdown_review.yaml["grade"],
        imdb_id=markdown_review.yaml["imdb_id"],
        review_content=markdown_review.review_content,
    )


def titles() -> Iterable[Title]:
    for json_title in json_titles.read_all():
        yield hydrate_json_title(json_title=json_title)


def viewings() -> Iterable[Viewing]:
    for json_viewing in json_viewings.read_all():
        yield hydrate_json_viewing(json_viewing=json_viewing)


def reviews() -> Iterable[Review]:
    for markdown_review in markdown_reviews.read_all():
        yield hydrate_markdown_review(markdown_review=markdown_review)


def update_datasets() -> None:
    (dataset_titles, dataset_names) = datasets_api.download_and_extract()

    db_api.update_titles_and_names(
        titles=list(dataset_titles.values()), names=list(dataset_names.values())
    )

    json_titles.update_for_datasets(dataset_titles=dataset_titles)
    json_metadata.update_for_datasets(dataset_titles=list(dataset_titles.values()))


def viewing_is_recent(viewing: Viewing) -> bool:
    return (datetime.date.today() - viewing.viewing_date).days < RECENT_VIEWING_DAYS


def recent_media() -> Sequence[str]:
    recent_viewings = filter(viewing_is_recent, viewings())

    return sorted(
        set([viewing.medium for viewing in recent_viewings if viewing.medium])
    )


def last_viewing_date() -> Optional[datetime.date]:
    sorted_viewings = sorted(
        viewings(), reverse=True, key=lambda viewing: viewing.sequence
    )

    return sorted_viewings[0].viewing_date if sorted_viewings else None
