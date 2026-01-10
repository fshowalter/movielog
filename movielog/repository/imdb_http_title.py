import json
from dataclasses import dataclass, field
from math import floor
from typing import Any, Literal, get_args

import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag
from requests.adapters import HTTPAdapter, Retry

from movielog.utils.get_nested_value import get_nested_value

type UntypedJson = dict[Any, Any]

TIMEOUT = 30

CreditKind = Literal["director", "writer", "performer"]

CREDIT_KINDS = get_args(CreditKind)

UNKNOWN_RELEASE_DATES = {
    "tt0273255": "1990-??-??",  # Hansel e Gretel
    "tt0150855": "1991-??-??",  # Hauntedween
    "tt0063183": "1968-??-??",  # Killer Darts
    "tt2087757": "1985-??-??",  # Faust
    "tt0097859": "1989-??-??",  # Il Mefistofele
}


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
    principal_cast: list[str]
    title: str
    year: int
    genres: list[str]
    countries: list[str]
    release_date: str
    release_date_country: str
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


def _parse_release_date_country(page_data: UntypedJson) -> str:
    country = get_nested_value(
        page_data, ["props", "pageProps", "mainColumnData", "releaseDate", "country", "text"]
    )

    if not isinstance(country, str):
        return "Unknown"

    return country


def _parse_release_date(imdb_id: str, page_data: UntypedJson) -> str:
    production_status_history = get_nested_value(
        page_data,
        ["props", "pageProps", "mainColumnData", "productionStatus", "productionStatusHistory"],
        [],
    )

    if not production_status_history:
        production_status_history = []

    production_status_history_release_date: str | None = next(
        (
            get_nested_value(history_item, ["date"], None)
            for history_item in production_status_history
            if get_nested_value(history_item, ["status", "id"], None) == "released"
        ),
        None,
    )

    if production_status_history_release_date:
        return production_status_history_release_date

    release_date = get_nested_value(
        page_data, ["props", "pageProps", "mainColumnData", "releaseDate"], None
    )

    if not release_date and imdb_id in UNKNOWN_RELEASE_DATES:
        return UNKNOWN_RELEASE_DATES[imdb_id]

    day = get_nested_value(release_date, ["day"], None)

    day = f"{day:02}" if isinstance(day, int) else "??"

    month = get_nested_value(release_date, ["month"], None)

    month = f"{month:02}" if isinstance(month, int) else "??"

    year = get_nested_value(release_date, ["year"], None)

    assert isinstance(year, int)

    return f"{year}-{month}-{day}"


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


def _parse_principal_cast(page_data: UntypedJson) -> list[str]:
    principal_cast = get_nested_value(
        page_data, ["props", "pageProps", "aboveTheFoldData", "castV2"], []
    )

    principal_credits = get_nested_value(principal_cast[0], ["credits"], [])

    return [get_nested_value(credit, ["name", "nameText", "text"]) for credit in principal_credits]


def _parse_countries(page_data: UntypedJson) -> list[str]:
    countries = get_nested_value(
        page_data, ["props", "pageProps", "mainColumnData", "countriesDetails", "countries"], []
    )

    return [country["text"] for country in countries]


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
        principal_cast=_parse_principal_cast(page_data),
        year=_parse_year(page_data),
        original_title=_parse_original_title(page_data),
        genres=_parse_genres(page_data),
        runtime_minutes=_parse_runtime_minutes(page_data),
        countries=_parse_countries(page_data),
        credits=_build_name_credits_for_title_page(page_data),
        release_date=_parse_release_date(imdb_id, page_data),
        release_date_country=_parse_release_date_country(page_data),
    )
