import datetime
from collections.abc import Generator, Iterable
from dataclasses import dataclass
from typing import get_args

from movielog.repository import (
    cast_and_crew_validator,
    imdb_http_person,
    imdb_http_title,
    imdb_ratings_data_updater,
    imdb_ratings_data_validator,
    json_cast_and_crew,
    json_collections,
    json_imdb_ratings,
    json_titles,
    json_watchlist_people,
    json_watchlist_person,
    markdown_reviews,
    markdown_viewings,
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
get_title_page = imdb_http_title.get_title_page
get_person_page = imdb_http_person.get_person_page


@dataclass
class CreditName:
    name: str
    imdb_id: str


@dataclass
class Title:
    imdb_id: str
    title: str
    sort_title: str
    release_year: str
    genres: list[str]
    runtime_minutes: int
    countries: list[str]
    directors: list[CreditName]
    performers: list[CreditName]
    writers: list[CreditName]
    original_title: str
    release_date: str
    slug: str


@dataclass
class Viewing:
    imdb_id: str
    sequence: int
    date: datetime.date
    medium: str | None
    venue: str | None
    medium_notes: str | None
    venue_notes: str | None


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

    def title(self, cache: list[Title] | None = None) -> Title:
        title_iterable = cache or titles()
        return next(title for title in title_iterable if title.imdb_id == self.imdb_id)


@dataclass
class WatchlistEntity:
    name: str
    slug: str
    title_ids: set[str]


@dataclass
class CastAndCrewMember:
    imdb_id: frozenset[str]
    name: str
    slug: str


@dataclass
class Collection:
    name: str
    slug: str
    title_ids: set[str]
    description: str


@dataclass
class WatchlistPerson(WatchlistEntity):
    imdb_id: frozenset[str]


def _hydrate_collection(
    json_collection: json_collections.JsonCollection,
) -> Collection:
    return Collection(
        name=json_collection["name"],
        slug=json_collection["slug"],
        title_ids={title["imdbId"] for title in json_collection["titles"]},
        description=json_collection["description"],
    )


def validate_data() -> None:
    title_data_validator.validate()
    cast_and_crew_validator.validate()
    imdb_ratings_data_validator.validate()


def collections() -> Generator[Collection]:
    for json_collection in json_collections.read_all():
        yield _hydrate_collection(json_collection)


def _hydrate_watchlist_person(
    json_watchlist_person: json_watchlist_person.JsonWatchlistPerson,
) -> WatchlistPerson:
    if isinstance(json_watchlist_person["imdbId"], list):
        imdb_id = frozenset(json_watchlist_person["imdbId"])
    else:
        imdb_id = frozenset((json_watchlist_person["imdbId"],))

    return WatchlistPerson(
        imdb_id=imdb_id,
        name=json_watchlist_person["name"],
        slug=json_watchlist_person["slug"],
        title_ids={title["imdbId"] for title in json_watchlist_person["titles"]},
    )


def _hydrate_cast_and_crew_member(
    json_cast_and_crew_member: json_cast_and_crew.JsonCastAndCrewMember,
) -> CastAndCrewMember:
    if isinstance(json_cast_and_crew_member["imdbId"], list):
        imdb_id = frozenset(json_cast_and_crew_member["imdbId"])
    else:
        imdb_id = frozenset((json_cast_and_crew_member["imdbId"],))

    return CastAndCrewMember(
        imdb_id=imdb_id,
        name=json_cast_and_crew_member["name"],
        slug=json_cast_and_crew_member["slug"],
    )


def cast_and_crew() -> Iterable[CastAndCrewMember]:
    for json_cast_and_crew_memenber in json_cast_and_crew.read_all():
        yield _hydrate_cast_and_crew_member(json_cast_and_crew_memenber)


def watchlist_people(
    kind: WatchlistPersonKind,
) -> Generator[WatchlistPerson]:
    for watchlist_person in json_watchlist_people.read_all(kind):
        yield _hydrate_watchlist_person(watchlist_person)


def titles() -> Iterable[Title]:
    for json_title in json_titles.read_all():
        yield Title(
            imdb_id=json_title["imdbId"],
            slug=json_title["slug"],
            title=json_title["title"],
            sort_title=json_title["sortTitle"],
            release_year=str(json_title["year"]),
            genres=json_title["genres"],
            original_title=json_title["originalTitle"],
            runtime_minutes=json_title["runtimeMinutes"],
            countries=json_title["countries"],
            release_date=json_title["releaseDate"],
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


def _hydrate_markdown_viewing(
    markdown_viewing: markdown_viewings.MarkdownViewing,
) -> Viewing:
    return Viewing(
        imdb_id=markdown_viewing["imdbId"],
        sequence=markdown_viewing["sequence"],
        medium=markdown_viewing["medium"],
        venue=markdown_viewing["venue"],
        date=markdown_viewing["date"],
        medium_notes=markdown_viewing["mediumNotes"],
        venue_notes=markdown_viewing["venueNotes"],
    )


def viewings() -> Iterable[Viewing]:
    for markdown_viewing in markdown_viewings.read_all():
        yield _hydrate_markdown_viewing(markdown_viewing)


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
    dataset_titles = datasets_api.download_and_extract()

    db_api.update_titles(titles=dataset_titles)

    imdb_ratings_data_updater.update_for_datasets(dataset_titles=dataset_titles)


@dataclass
class TitleImdbRating:
    imdb_id: str
    votes: int | None
    rating: float | None


@dataclass
class ImdbRatings:
    average_imdb_votes: float
    average_imdb_rating: float
    titles: list[TitleImdbRating]


def imdb_ratings() -> ImdbRatings:
    json_ratings = json_imdb_ratings.deserialize()

    title_ratings = []

    for imdb_id, rating in json_ratings["titles"].items():
        title_ratings.append(
            TitleImdbRating(imdb_id=imdb_id, votes=rating["votes"], rating=rating["rating"])
        )

    return ImdbRatings(
        average_imdb_rating=json_ratings["averageImdbRating"],
        average_imdb_votes=json_ratings["averageImdbVotes"],
        titles=title_ratings,
    )


def create_viewing(
    imdb_id: str,
    full_title: str,
    date: datetime.date,
    medium: str | None,
    venue: str | None,
    medium_notes: str | None,
) -> Viewing:
    return _hydrate_markdown_viewing(
        markdown_viewings.create(
            imdb_id=imdb_id,
            full_title=full_title,
            date=date,
            medium=medium,
            venue=venue,
            medium_notes=medium_notes,
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


def new_collection(name: str, description: str) -> Collection:
    return _hydrate_collection(json_collections.create(name, description))


def add_person_to_watchlist(
    watchlist: WatchlistPersonKind, imdb_id: str, name: str
) -> WatchlistPerson:
    return _hydrate_watchlist_person(json_watchlist_people.create(watchlist, imdb_id, name))


def add_title_to_collection(collection: Collection, imdb_id: str, full_title: str) -> Collection:
    return _hydrate_collection(
        json_collections.add_title(
            collection_slug=collection.slug, imdb_id=imdb_id, full_title=full_title
        )
    )
