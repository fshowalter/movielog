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


@dataclass(frozen=True)
class TitleCredit:
    imdb_id: str
    full_title: str
    title_type: str | None
    role: str | None
    attributes: tuple[str] | None


@dataclass
class ImdbPerson:
    imdb_id: str
    credits: list[TitleCredit]


@dataclass
class PersonPage:
    imdb_id: str
    name: str
    known_for_titles: list[str]


type UntypedJson = dict[Any, Any]


def title_credit_for_edge(edge: UntypedJson) -> TitleCredit:
    title = get_nested_value(edge, ["node", "title", "titleText", "text"])
    year = get_nested_value(edge, ["node", "title", "releaseYear", "year"])

    roles = get_nested_value(edge, ["node", "creditedRoles", "edges"], [{}])

    role = get_nested_value(roles[0], ["node", "text"], None)

    return TitleCredit(
        imdb_id=get_nested_value(edge, ["node", "title", "id"]),
        full_title=f"{title} ({year})",
        title_type=get_nested_value(edge, ["node", "title", "titleType", "text"])
        if get_nested_value(edge, ["node", "title", "titleType", "text"]) != "Movie"
        else None,
        role=role,
        attributes=tuple(
            attribute["text"] for attribute in get_nested_value(roles[0], ["node", "attributes"])
        )
        if get_nested_value(roles[0], ["node", "attributes"])
        else None,
    )


def _edge_title_is_released(edge: UntypedJson) -> bool:
    title_kind: str = get_nested_value(
        edge, ["node", "title", "productionStatus", "currentProductionStage", "id"]
    )

    return title_kind == "released"


def _edge_title_is_valid_type(edge: UntypedJson) -> bool:
    title_type = get_nested_value(edge, ["node", "title", "titleType", "id"])

    return title_type in ("movie", "tvMovie", "video")


def _edge_title_release_year_is_not_1927_or_later(edge: UntypedJson) -> bool:
    title_year: int = get_nested_value(edge, ["node", "title", "releaseYear", "year"])

    return title_year >= 1927


def _edge_title_is_at_least_40_minutes(edge: UntypedJson) -> bool:
    runtime_in_seconds: int = get_nested_value(edge, ["node", "title", "runtime", "seconds"], 0)

    return runtime_in_seconds >= 2400


def _edge_title_has_no_invalid_genres(edge: UntypedJson) -> bool:
    genres = {
        get_nested_value(genre, ["genre", "text"])
        for genre in get_nested_value(edge, ["node", "title", "titleGenres", "genres"], [])
    }

    return len(set.intersection({"Adult", "Documentary", "Short"}, genres)) == 0


def edge_is_valid_title(edge: UntypedJson) -> bool:
    return (
        _edge_title_is_released(edge)
        and _edge_title_is_valid_type(edge)
        and _edge_title_has_no_invalid_genres(edge)
        and _edge_title_release_year_is_not_1927_or_later(edge)
        and _edge_title_is_at_least_40_minutes(edge)
    )


def session_get(session: requests.Session, url: str, *, json: bool = False) -> requests.Response:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",  # noqa: E501
        "Accept-Language": "en-US,en;q=0.5",
    }

    if json:
        headers["content-type"] = "application/json"

    return session.get(
        url,
        headers=headers,
        timeout=TIMEOUT,
    )


def call_graphql(
    session: requests.Session, operation: str, variables: UntypedJson, extensions: UntypedJson
) -> UntypedJson:
    query_variables = json.dumps(variables)

    query_extensions = json.dumps(extensions)

    url = f"https://caching.graphql.imdb.com/?operationName={operation}&variables={query_variables}&extensions={query_extensions}"

    response = session_get(url=url, session=session, json=True)

    response_data = json.loads(response.text)

    assert isinstance(response_data, dict)

    return response_data


def create_session() -> requests.Session:
    session = requests.Session()

    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])

    session.mount("https://", HTTPAdapter(max_retries=retries))

    return session


def _get_person_data(session: requests.Session, imdb_id: str) -> UntypedJson:
    if not session:
        session = create_session()

    page = session_get(session=session, url=f"https://www.imdb.com/name/{imdb_id}/")

    soup = BeautifulSoup(
        page.text, "html.parser", parse_only=SoupStrainer("script", id="__NEXT_DATA__")
    )

    script_tag = soup.find("script", id="__NEXT_DATA__")

    assert script_tag

    assert isinstance(script_tag, Tag)

    page_data = json.loads(str(script_tag.string))

    assert isinstance(page_data, dict)

    return page_data


def _parse_known_for_titles(page_data: UntypedJson) -> list[str]:
    known_for_credits = get_nested_value(
        page_data, ["props", "pageProps", "aboveTheFold", "knownForV2", "credits"], []
    )

    return [
        get_nested_value(credit, ["title", "titleText", "text"]) for credit in known_for_credits
    ]


def get_person_page(imdb_id: str) -> PersonPage:
    session = create_session()

    page_data = _get_person_data(session, imdb_id)

    return PersonPage(
        imdb_id=imdb_id,
        name=get_nested_value(
            page_data, ["props", "pageProps", "aboveTheFold", "nameText", "text"]
        ),
        known_for_titles=_parse_known_for_titles(page_data),
    )


def get_credits(session: requests.Session, imdb_id: str) -> list[UntypedJson]:
    page_data = _get_person_data(session, imdb_id)

    edges = get_nested_value(
        page_data, ["props", "pageProps", "mainColumnData", "released", "edges"]
    )

    assert isinstance(edges, list)

    return edges
