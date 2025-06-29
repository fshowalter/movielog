import json
from dataclasses import dataclass, field
from typing import Any, Literal, get_args

import pycountry
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
    production_status: str | None
    kind: str
    credits: dict[CreditKind, list[NameCredit]]
    full_title: str
    genres: list[str]
    countries: list[str]
    sound_mix: set[str]
    release_date: str


def _build_name_credits_for_title_page(
    page_data: UntypedJson,
) -> dict[CreditKind, list[NameCredit]]:
    credit_kind_map: dict[CreditKind, str] = {
        "director": "director",
        "performer": "cast",
        "writer": "writer",
    }

    name_credits: dict[CreditKind, list[NameCredit]] = {}

    credit_categories = get_nested_value(
        page_data, ["props", "pageProps", "mainColumnData", "categories"], []
    )

    for credit_kind, category_id in credit_kind_map.items():
        name_credits[credit_kind] = []

        imdb_credits = next(
            get_nested_value(credit_category, ["section", "items"], [])
            for credit_category in credit_categories
            if credit_category["id"] == category_id
        )

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


def _parse_production_status(page_data: UntypedJson) -> str | None:
    status = get_nested_value(
        page_data,
        [
            "props",
            "pageProps",
            "mainColumnData",
            "productionStatus",
            "currentProductionStage",
            "id",
        ],
        None,
    )

    assert isinstance(status, str | None)

    return status


def _parse_title(page_data: UntypedJson) -> str:
    title = get_nested_value(
        page_data, ["props", "pageProps", "mainColumnData", "titleText", "text"], None
    )

    assert isinstance(title, str)

    return title


def _parse_year(page_data: UntypedJson) -> int:
    year = get_nested_value(
        page_data, ["props", "pageProps", "mainColumnData", "releaseYear", "year"], None
    )

    assert isinstance(year, int)

    return year


def _parse_kind(page_data: UntypedJson) -> str:
    kind = get_nested_value(
        page_data, ["props", "pageProps", "mainColumnData", "titleType", "id"], "Unknown"
    )

    assert isinstance(kind, str)

    return kind


def _parse_genres(page_data: UntypedJson) -> list[str]:
    genres = get_nested_value(
        page_data, ["props", "pageProps", "mainColumnData", "genres", "genres"], []
    )

    return [genre["text"] for genre in genres]


def _parse_countries(page_data: UntypedJson) -> list[str]:
    countries = get_nested_value(
        page_data, ["props", "pageProps", "mainColumnData", "countriesOfOrigin", "countries"], []
    )

    return [pycountry.countries.get(alpha_2=country["id"]).name for country in countries]


def _parse_sound_mix(page_data: UntypedJson) -> set[str]:
    sound_mixes = get_nested_value(
        page_data,
        ["props", "pageProps", "mainColumnData", "technicalSpecifications", "soundMixes", "item"],
        [],
    )

    return {mix["text"] for mix in sound_mixes}


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
        production_status=_parse_production_status(page_data),
        kind=_parse_kind(page_data),
        full_title=_parse_title(page_data),
        genres=_parse_genres(page_data),
        countries=_parse_countries(page_data),
        sound_mix=_parse_sound_mix(page_data),
        credits=_build_name_credits_for_title_page(page_data),
        release_date=get_release_date(imdb_id, _parse_year(page_data)),
    )
