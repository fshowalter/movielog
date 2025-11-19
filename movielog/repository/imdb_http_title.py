import json
from dataclasses import dataclass, field
from math import floor
from typing import Any, Literal, get_args

import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag
from requests.adapters import HTTPAdapter, Retry

from movielog.repository.imdb_http_release_date import get_release_date
from movielog.utils.get_nested_value import get_nested_value

type UntypedJson = dict[Any, Any]

TIMEOUT = 30

CreditKind = Literal["director", "writer", "performer"]

CREDIT_KINDS = get_args(CreditKind)


@dataclass
class NameCredit:
    kind: CreditKind
    sequence: int
    imdb_id: str
    name: str
    notes: str | None = None
    roles: list[str] = field(default_factory=list)


@dataclass
class TitlePage:
    imdb_id: str
    credits: dict[CreditKind, list[NameCredit]]
    title: str
    year: int
    genres: list[str]
    countries: list[str]
    release_date: str
    aggregate_rating: float
    vote_count: int
    runtime_minutes: int
    original_title: str


def _build_name_credits_for_title_page(
    page_data: UntypedJson,
) -> dict[CreditKind, list[NameCredit]]:
    credit_kind_map: dict[CreditKind, set[str]] = {
        "director": {
            "amzn1.imdb.concept.name_credit_category.ace5cb4c-8708-4238-9542-04641e7c8171",
            "director",
        },
        "performer": {
            "amzn1.imdb.concept.name_credit_group.7caf7d16-5db9-4f4f-8864-d4c6e711c686",
            "cast",
        },
        "writer": {
            "amzn1.imdb.concept.name_credit_category.c84ecaff-add5-4f2e-81db-102a41881fe3",
            "writer",
        },
    }

    name_credits: dict[CreditKind, list[NameCredit]] = {}

    credit_categories = get_nested_value(
        page_data, ["props", "pageProps", "mainColumnData", "categories"], []
    )

    for credit_kind, category_id in credit_kind_map.items():
        name_credits[credit_kind] = []

        try:
            imdb_credits = next(
                get_nested_value(credit_category, ["section", "items"], [])
                for credit_category in credit_categories
                if credit_category["id"] in category_id
            )
        except StopIteration:
            print(credit_categories)
            raise

        for index, imdb_credit in enumerate(imdb_credits):
            name_credit = NameCredit(
                sequence=index,
                kind=credit_kind,
                imdb_id=imdb_credit["id"],
                name=imdb_credit["rowTitle"],
                notes=imdb_credit.get("attributes", None),
            )

            if credit_kind == "performer":
                name_credit.roles = imdb_credit.get("characters", [])

            name_credits[credit_kind].append(name_credit)

    return name_credits


def _parse_title(page_data: UntypedJson) -> str:
    title = get_nested_value(
        page_data, ["props", "pageProps", "aboveTheFoldData", "titleText", "text"], None
    )

    assert isinstance(title, str)

    return title


def _parse_original_title(page_data: UntypedJson) -> str:
    title = get_nested_value(
        page_data, ["props", "pageProps", "aboveTheFoldData", "originalTitleText", "text"], None
    )

    assert isinstance(title, str)

    return title


def _parse_year(page_data: UntypedJson) -> int:
    year = get_nested_value(
        page_data, ["props", "pageProps", "aboveTheFoldData", "releaseYear", "year"], None
    )

    assert isinstance(year, int)

    return year


def _parse_genres(page_data: UntypedJson) -> list[str]:
    genres = get_nested_value(
        page_data, ["props", "pageProps", "mainColumnData", "genres", "genres"], []
    )

    return [genre["text"] for genre in genres]


def _parse_countries(page_data: UntypedJson) -> list[str]:
    countries = get_nested_value(
        page_data, ["props", "pageProps", "mainColumnData", "countriesDetails", "countries"], []
    )

    return [country["text"] for country in countries]


def _parse_aggregate_rating(page_data: UntypedJson) -> float:
    return float(
        get_nested_value(
            page_data,
            ["props", "pageProps", "aboveTheFoldData", "ratingsSummary", "aggregateRating"],
        )
    )


def _parse_vote_count(page_data: UntypedJson) -> int:
    vote_count = get_nested_value(
        page_data, ["props", "pageProps", "aboveTheFoldData", "ratingsSummary", "voteCount"]
    )

    assert isinstance(vote_count, int)

    return vote_count


def _parse_runtime_minutes(page_data: UntypedJson) -> int:
    runtime_seconds = get_nested_value(
        page_data, ["props", "pageProps", "aboveTheFoldData", "runtime", "seconds"]
    )

    assert isinstance(runtime_seconds, int)

    return floor(runtime_seconds / 60)


def get_title_page(imdb_id: str) -> TitlePage:
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])

    session.mount("https://", HTTPAdapter(max_retries=retries))

    page = session.get(
        f"https://www.imdb.com/title/{imdb_id}/reference",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",  # noqa: E501
            "Accept-Language": "en-US,en;q=0.5",
        },
        timeout=TIMEOUT,
    )

    soup = BeautifulSoup(
        page.text, "html.parser", parse_only=SoupStrainer("script", id="__NEXT_DATA__")
    )

    script_tag = soup.find("script", id="__NEXT_DATA__")

    assert script_tag

    assert isinstance(script_tag, Tag)

    page_data = json.loads(str(script_tag.string))

    assert isinstance(page_data, dict)

    return TitlePage(
        imdb_id=imdb_id,
        title=_parse_title(page_data),
        year=_parse_year(page_data),
        original_title=_parse_original_title(page_data),
        genres=_parse_genres(page_data),
        runtime_minutes=_parse_runtime_minutes(page_data),
        countries=_parse_countries(page_data),
        credits=_build_name_credits_for_title_page(page_data),
        release_date=get_release_date(imdb_id, _parse_year(page_data)),
        aggregate_rating=_parse_aggregate_rating(page_data),
        vote_count=_parse_vote_count(page_data),
    )
