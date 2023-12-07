import datetime
from dataclasses import dataclass
from typing import Iterable, Optional, Sequence, Union, get_args

from movielog.repository import (
    json_metadata,
    json_titles,
    json_viewings,
    json_watchlist_collections,
    json_watchlist_people,
    markdown_reviews,
    title_data_updater,
    watchlist_credits_updater,
)
from movielog.repository.datasets import api as datasets_api
from movielog.repository.db import api as db_api

RECENT_VIEWING_DAYS = 365

WatchlistPersonKind = json_watchlist_people.Kind

WATCHLIST_PERSON_KINDS = get_args(WatchlistPersonKind)

db = db_api.db

update_watchlist_credits = watchlist_credits_updater.update_watchlist_credits
update_title_data = title_data_updater.update_title_data


@dataclass
class Name(object):
    name: str
    imdb_id: str


@dataclass
class Title(object):
    imdb_id: str
    title: str
    sort_title: str
    year: str
    genres: list[str]
    runtime_minutes: int
    countries: list[str]
    directors: list[Name]
    performers: list[Name]
    writers: list[Name]
    original_title: str
    imdb_rating: Optional[float]
    imdb_votes: Optional[int]

    @property
    def year_and_imdb_id(self) -> str:
        return "{0}{1}".format(self.year, self.imdb_id)


@dataclass
class Viewing(object):
    imdb_id: str
    sequence: int
    date: datetime.date
    medium: Optional[str]
    venue: Optional[str]
    medium_notes: Optional[str]


@dataclass
class Review(object):
    imdb_id: str
    slug: str
    grade: str
    date: datetime.date

    @property
    def grade_value(self) -> int:
        assert self.grade

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

    def title(self, cache: Optional[list[Title]] = None) -> Title:
        title_iterable = cache or titles()
        return next(title for title in title_iterable if title.imdb_id == self.imdb_id)


@dataclass
class WatchlistEntity(object):
    name: str
    slug: str
    title_ids: set[str]


@dataclass
class WatchlistCollection(WatchlistEntity):
    description: Optional[str] = None


@dataclass
class WatchlistPerson(WatchlistEntity):
    imdb_id: Union[str, list[str]]


def watchlist_collections() -> list[WatchlistCollection]:
    for json_watchlist_collection in json_watchlist_collections.read_all():
        yield WatchlistCollection(
            name=json_watchlist_collection["name"],
            slug=json_watchlist_collection["slug"],
            title_ids=set(
                [title["imdbId"] for title in json_watchlist_collection["titles"]]
            ),
        )


def watchlist_people(kind: WatchlistPersonKind) -> list[WatchlistPerson]:
    for json_watchlist_person in json_watchlist_people.read_all(kind):
        yield WatchlistPerson(
            imdb_id=json_watchlist_person["imdbId"],
            name=json_watchlist_person["name"],
            slug=json_watchlist_person["slug"],
            title_ids=set(
                [title["imdbId"] for title in json_watchlist_person["titles"]]
            ),
        )


def titles() -> Iterable[Title]:
    for json_title in json_titles.read_all():
        yield Title(
            imdb_id=json_title["imdbId"],
            title=json_title["title"],
            sort_title=json_title["sortTitle"],
            year=str(json_title["year"]),
            genres=json_title["genres"],
            original_title=json_title["originalTitle"],
            runtime_minutes=json_title["runtimeMinutes"],
            countries=json_title["countries"],
            imdb_rating=json_title["imdbRating"],
            imdb_votes=json_title["imdbVotes"],
            directors=[
                Name(
                    name=director["name"],
                    imdb_id=director["imdbId"],
                )
                for director in json_title["directors"]
            ],
            performers=[
                Name(
                    name=performer["name"],
                    imdb_id=performer["imdbId"],
                )
                for performer in json_title["performers"]
            ],
            writers=[
                Name(
                    name=writer["name"],
                    imdb_id=writer["imdbId"],
                )
                for writer in json_title["writers"]
            ],
        )


def _hydrate_json_viewing(json_viewing: json_viewings.JsonViewing) -> Viewing:
    return Viewing(
        imdb_id=json_viewing["imdbId"],
        sequence=json_viewing["sequence"],
        medium=json_viewing["medium"],
        venue=json_viewing["medium"],
        date=datetime.date.fromisoformat(json_viewing["date"]),
        medium_notes=json_viewing["mediumNotes"],
    )


def viewings() -> Iterable[Viewing]:
    for json_viewing in json_viewings.read_all():
        yield _hydrate_json_viewing(json_viewing)


def _hydrate_markdown_review(
    markdown_review: markdown_reviews.MarkdownReview,
) -> Review:
    return Review(
        slug=markdown_review.yaml["slug"],
        date=markdown_review.yaml["date"],
        grade=markdown_review.yaml["grade"],
        imdb_id=markdown_review.yaml["imdb_id"],
    )


def reviews() -> Iterable[Review]:
    for markdown_review in markdown_reviews.read_all():
        yield _hydrate_markdown_review(markdown_review)


def update_datasets() -> None:
    (dataset_titles, dataset_names) = datasets_api.download_and_extract()

    db_api.update_titles_and_names(
        titles=list(dataset_titles.values()), names=list(dataset_names.values())
    )

    json_titles.update_for_datasets(dataset_titles=dataset_titles)
    json_metadata.update_for_datasets(dataset_titles=list(dataset_titles.values()))


def _viewing_is_recent(viewing: Viewing) -> bool:
    return (datetime.date.today() - viewing.date).days < RECENT_VIEWING_DAYS


def recent_media() -> Sequence[str]:
    recent_viewings = filter(_viewing_is_recent, viewings())

    return sorted(
        set([viewing.medium for viewing in recent_viewings if viewing.medium])
    )


def last_viewing_date() -> Optional[datetime.date]:
    sorted_viewings = sorted(
        viewings(), reverse=True, key=lambda viewing: viewing.sequence
    )

    return sorted_viewings[0].date if sorted_viewings else None


@dataclass
class Metadata(object):
    average_imdb_votes: float
    average_imdb_rating: float


def metadata() -> Metadata:
    json_metadata_info = json_metadata.deserialize()
    return Metadata(
        average_imdb_rating=json_metadata_info["averageImdbRating"],
        average_imdb_votes=json_metadata_info["averageImdbVotes"],
    )


def create_viewing(
    imdb_id: str,
    full_title: str,
    date: datetime.date,
    medium: str,
) -> Viewing:
    return _hydrate_json_viewing(
        json_viewings.create(
            imdb_id=imdb_id,
            full_title=full_title,
            date=date.isoformat(),
            medium=medium,
        )
    )


def create_or_update_review(
    imdb_id: str, full_title: str, date: datetime.date, grade: str
) -> Review:
    return _hydrate_markdown_review(
        markdown_reviews.create_or_update(
            imdb_id=imdb_id, full_title=full_title, date=date, grade=grade
        )
    )
