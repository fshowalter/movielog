import json
from dataclasses import dataclass
from typing import Any, Literal, get_args

import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag
from requests.adapters import HTTPAdapter, Retry

from movielog.utils.get_nested_value import get_nested_value

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


type UntypedJson = dict[Any, Any]


def _build_title_credits_for_name_page(
    page_data: UntypedJson,
) -> dict[CreditKind, list[TitleCredit]]:
    credit_kind_map: dict[CreditKind, list[str]] = {
        "director": ["director"],
        "performer": ["actor", "actress"],
        "writer": ["writer"],
    }

    name_credits: dict[CreditKind, list[TitleCredit]] = {}

    for kind in CREDIT_KINDS:
        credit_keys = credit_kind_map[kind]
        name_credits[kind] = []

        for credit_key in credit_keys:
            edges: list[Any] = next(
                (
                    get_nested_value(imdb_credits, ["credits", "edges"], [])
                    for imdb_credits in get_nested_value(
                        page_data,
                        ["props", "pageProps", "mainColumnData", "releasedPrimaryCredits"],
                    )
                    if imdb_credits["category"]["id"] == credit_key
                ),
                [],
            )

            title_credits = [
                TitleCredit(
                    kind=kind,
                    imdb_id=get_nested_value(edge, ["node", "title", "id"]),
                    full_title=get_nested_value(edge, ["node", "title", "titleText", "text"]),
                )
                for edge in edges
            ]

            name_credits[kind].extend(title_credit for title_credit in title_credits)

    return name_credits


def get_name_page(imdb_id: str) -> NamePage:
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])

    session.mount("https://", HTTPAdapter(max_retries=retries))

    page = session.get(
        f"https://www.imdb.com/name/{imdb_id}/",
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

    return NamePage(credits=_build_title_credits_for_name_page(page_data))
