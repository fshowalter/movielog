import json
from dataclasses import dataclass
from typing import Any, Literal, get_args

import requests
from requests.adapters import HTTPAdapter, Retry

from movielog.utils.get_nested_value import get_nested_value

TIMEOUT = 30

CreditKind = Literal["director", "writer", "performer"]

CREDIT_KINDS = get_args(CreditKind)


@dataclass(frozen=True)
class TitleCredit:
    imdb_id: str
    full_title: str


@dataclass
class PersonPage:
    imdb_id: str
    credits: list[TitleCredit]


type UntypedJson = dict[Any, Any]


def title_credit_for_edge(edge: UntypedJson) -> TitleCredit:
    kind_suffix = {
        "tvMovie": " (TV)",
        "video": " (V)",
    }

    title = get_nested_value(edge, ["node", "title", "titleText", "text"])
    year = get_nested_value(edge, ["node", "title", "releaseYear", "year"])
    kind = kind_suffix.get(get_nested_value(edge, ["node", "title", "titleType", "id"]), "")

    return TitleCredit(
        imdb_id=get_nested_value(edge, ["node", "title", "id"]),
        full_title=f"{title} ({year}){kind}",
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


def _edge_title_has_no_invalid_genres(edge: UntypedJson) -> bool:
    genres = (
        get_nested_value(genre, ["genre", "text"])
        for genre in get_nested_value(edge, ["node", "title", "titleGenres", "genres"], [])
    )

    return len(set.intersection({"Adult", "Documentary", "Short"}, genres)) == 0


def edge_is_valid_title(edge: UntypedJson) -> bool:
    return (
        _edge_title_is_released(edge)
        & _edge_title_is_valid_type(edge)
        & _edge_title_has_no_invalid_genres(edge)
        & _edge_title_release_year_is_not_1927_or_later(edge)
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


def get_credits(session: requests.Session, imdb_id: str) -> UntypedJson:
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])

    session.mount("https://", HTTPAdapter(max_retries=retries))

    session_get(session=session, url=f"https://www.imdb.com/name/{imdb_id}/")

    credits_variables = {"id": imdb_id, "includeUserRating": False, "locale": "en-US"}

    credits_extensions = {
        "persistedQuery": {
            "sha256Hash": "47ffacde22ede1b84480c604ae6cda83362ff6e4a033dd105853670fa5a0ed56",
            "version": 1,
        }
    }

    return call_graphql(
        session=session,
        operation="NameMainFilmographyFilteredCredits",
        variables=credits_variables,
        extensions=credits_extensions,
    )
