import datetime
from dataclasses import dataclass
from typing import Generator, Iterable, Optional, Union, get_args

from movielog.repository import (  # noqa: WPS235
    json_metadata,
    json_names,
    json_titles,
    json_viewings,
    json_watchlist_collections,
    json_watchlist_people,
    markdown_reviews,
    name_data_validator,
    title_data_updater,
    title_data_validator,
    watchlist_credits_updater,
)
from movielog.repository.datasets import api as datasets_api
from movielog.repository.db import api as db_api

WatchlistPersonKind = json_watchlist_people.Kind

WATCHLIST_PERSON_KINDS = get_args(WatchlistPersonKind)

db = db_api.db

update_watchlist_credits = watchlist_credits_updater.update_watchlist_credits
update_title_data = title_data_updater.update_from_imdb_pages


@dataclass
class CreditName:
    name: str
    imdb_id: str


@dataclass
class Title:
    imdb_id: str
    title: str
    sort_title: str
    year: str
    genres: list[str]
    runtime_minutes: int
    countries: list[str]
    directors: list[CreditName]
    performers: list[CreditName]
    writers: list[CreditName]
    original_title: str
    imdb_rating: Optional[float]
    imdb_votes: Optional[int]
    release_sequence: str


@dataclass
class Viewing:
    imdb_id: str
    sequence: int
    date: datetime.date
    medium: Optional[str]
    venue: Optional[str]
    medium_notes: Optional[str]
    venue_notes: Optional[str]


@dataclass
class Name:
    imdb_id: str | list[str]
    name: str
    slug: str


@dataclass
class Review:
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
class WatchlistEntity:
    name: str
    slug: str
    title_ids: set[str]


@dataclass
class WatchlistCollection(WatchlistEntity):
    description: Optional[str] = None


@dataclass
class WatchlistPerson(WatchlistEntity):
    imdb_id: Union[str, list[str]]


def _hydrate_watchlist_collection(
    json_watchlist_collection: json_watchlist_collections.JsonWatchlistCollection,
) -> WatchlistCollection:
    return WatchlistCollection(
        name=json_watchlist_collection["name"],
        slug=json_watchlist_collection["slug"],
        title_ids=set(
            [title["imdbId"] for title in json_watchlist_collection["titles"]]
        ),
    )


def validate_data() -> None:
    title_data_validator.validate()
    name_data_validator.validate()


def watchlist_collections() -> Generator[WatchlistCollection, None, None]:
    for json_watchlist_collection in json_watchlist_collections.read_all():
        yield _hydrate_watchlist_collection(json_watchlist_collection)


def _hydrate_watchlist_person(
    json_watchlist_person: json_watchlist_people.JsonWatchlistPerson,
) -> WatchlistPerson:
    return WatchlistPerson(
        imdb_id=json_watchlist_person["imdbId"],
        name=json_watchlist_person["name"],
        slug=json_watchlist_person["slug"],
        title_ids=set([title["imdbId"] for title in json_watchlist_person["titles"]]),
    )


def names() -> Iterable[Name]:
    for json_name in json_names.read_all():
        yield Name(
            imdb_id=json_name["imdbId"], name=json_name["name"], slug=json_name["slug"]
        )


def watchlist_people(
    kind: WatchlistPersonKind,
) -> Generator[WatchlistPerson, None, None]:
    for json_watchlist_person in json_watchlist_people.read_all(kind):
        yield _hydrate_watchlist_person(json_watchlist_person)


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
            release_sequence="{0}{1}".format(
                json_title["releaseDate"], json_title["imdbId"]
            ),
            directors=[
                CreditName(
                    name=director["name"],
                    imdb_id=director["imdbId"],
                )
                for director in json_title["directors"]
            ],
            performers=[
                CreditName(
                    name=performer["name"],
                    imdb_id=performer["imdbId"],
                )
                for performer in json_title["performers"]
            ],
            writers=[
                CreditName(
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
        venue=json_viewing["venue"],
        date=datetime.date.fromisoformat(json_viewing["date"]),
        medium_notes=json_viewing["mediumNotes"],
        venue_notes=json_viewing["venueNotes"],
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

    title_data_updater.update_for_datasets(dataset_titles=dataset_titles)
    json_metadata.update_for_datasets(dataset_titles=list(dataset_titles.values()))


@dataclass
class Metadata:
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
    medium: Optional[str],
    venue: Optional[str],
) -> Viewing:
    return _hydrate_json_viewing(
        json_viewings.create(
            imdb_id=imdb_id,
            full_title=full_title,
            date=date.isoformat(),
            medium=medium,
            venue=venue,
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


def new_watchlist_collection(name: str) -> WatchlistCollection:
    return _hydrate_watchlist_collection(json_watchlist_collections.create(name))


def add_person_to_watchlist(
    watchlist: WatchlistPersonKind, imdb_id: str, name: str
) -> WatchlistPerson:
    return _hydrate_watchlist_person(
        json_watchlist_people.create(watchlist, imdb_id, name)
    )


def add_title_to_collection(
    collection: WatchlistCollection, imdb_id: str, full_title: str
) -> WatchlistCollection:
    return _hydrate_watchlist_collection(
        json_watchlist_collections.add_title(
            collection_slug=collection.slug, imdb_id=imdb_id, full_title=full_title
        )
    )
