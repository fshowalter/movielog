import json
from dataclasses import dataclass, field
from typing import Literal, get_args

import imdb
import pycountry
import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag
from requests.adapters import HTTPAdapter, Retry

from movielog.repository.imdb_http_release_date import get_release_date

imdb_http = imdb.Cinemagoer(reraiseExceptions=True)


TIMEOUT = 30

CreditKind = Literal["director", "writer", "performer"]

CREDIT_KINDS = get_args(CreditKind)


@dataclass
class TitleCredit:
    kind: CreditKind
    imdb_id: str
    full_title: str


@dataclass
class NamePage:
    credits: dict[CreditKind, list[TitleCredit]]


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


def _build_title_credits_for_name_page(
    imdb_name_page: imdb.Person.Person,
) -> dict[CreditKind, list[TitleCredit]]:
    name_credits = {}

    filmography = imdb_name_page["filmography"]

    filmography["performer"] = filmography.pop(
        "actor",
        [],
    ) + filmography.pop(
        "actress",
        [],
    )

    for kind in CREDIT_KINDS:
        name_credits[kind] = [
            TitleCredit(
                kind=kind,
                imdb_id=f"tt{credit.movieID}",
                full_title=credit["long imdb title"],
            )
            for credit in imdb_name_page["filmography"].get(kind, [])
        ]

    return name_credits


def _build_name_credits_for_title_page(
    page_data: dict,
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


def get_nested_value(dict_obj, keys, default=None):
    """Safely get nested dictionary values."""
    current = dict_obj
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key, default)
        else:
            return default
    return current


def get_name_page(imdb_id: str) -> NamePage:
    imdb_name_page = imdb_http.get_person(imdb_id[2:])

    return NamePage(credits=_build_title_credits_for_name_page(imdb_name_page))


def parse_production_status(page_data: dict) -> str | None:
    return get_nested_value(
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


def parse_title(page_data: dict) -> str:
    title = get_nested_value(
        page_data, ["props", "pageProps", "mainColumnData", "titleText", "text"], None
    )

    assert title

    return title


def parse_year(page_data: dict) -> str:
    year = get_nested_value(
        page_data, ["props", "pageProps", "mainColumnData", "releaseYear", "year"], None
    )

    assert year

    return year


def parse_kind(page_data: dict) -> str:
    return get_nested_value(
        page_data, ["props", "pageProps", "mainColumnData", "titleType", "id"], "Unknown"
    )


def parse_genres(page_data: dict) -> list[str]:
    genres = get_nested_value(
        page_data, ["props", "pageProps", "mainColumnData", "genres", "genres"], []
    )

    return [genre["text"] for genre in genres]


def parse_countries(page_data: dict) -> list[str]:
    countries = get_nested_value(
        page_data, ["props", "pageProps", "mainColumnData", "countriesOfOrigin", "countries"], []
    )

    return [pycountry.countries.get(alpha_2=country["id"]).name for country in countries]


def parse_sound_mix(page_data: dict) -> set[str]:
    sound_mixes = get_nested_value(
        page_data,
        ["props", "pageProps", "mainColumnData", "technicalSpecifications", "soundMixes", "item"],
        [],
    )

    return [mix["text"] for mix in sound_mixes]


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
        production_status=parse_production_status(page_data),
        kind=parse_kind(page_data),
        full_title=parse_title(page_data),
        genres=parse_genres(page_data),
        countries=parse_countries(page_data),
        sound_mix=parse_sound_mix(page_data),
        credits=_build_name_credits_for_title_page(page_data),
        release_date=get_release_date(imdb_id, parse_year(page_data)),
    )
