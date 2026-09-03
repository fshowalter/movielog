import json
from collections.abc import Callable
from typing import Any

import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag
from requests.adapters import HTTPAdapter, Retry

from movielog.utils.logging import logger

TIMEOUT = 30

Session = requests.Session

type UntypedJson = dict[Any, Any]

GetToken = Callable[[], str | None]


class TokenPromptCancelledError(Exception):
    pass


class ImdbSession:
    def __init__(self, session: requests.Session, get_token: GetToken) -> None:
        self.session = session
        self._get_token = get_token

    def refresh_token(self) -> None:
        token = self._get_token()

        if token is None:
            raise TokenPromptCancelledError

        self.session.cookies["aws-waf-token"] = token


def create_session(get_token: GetToken) -> ImdbSession:
    token = get_token()

    if token is None:
        raise TokenPromptCancelledError

    session = requests.Session()

    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])

    session.mount("https://", HTTPAdapter(max_retries=retries))

    if token:
        session.cookies["aws-waf-token"] = token

    return ImdbSession(session=session, get_token=get_token)


def session_get(session: requests.Session, url: str, *, json: bool = False) -> requests.Response:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:151.0) Gecko/20100101 Firefox/151.0",  # noqa: E501
        "Accept-Language": "en-US,en;q=0.9",
    }

    if json:
        headers["content-type"] = "application/json"

    return session.get(
        url,
        headers=headers,
        timeout=TIMEOUT,
    )


def _fetch_next_data_script_tag(session: requests.Session, url: str) -> Tag | None:
    page = session_get(session=session, url=url)

    soup = BeautifulSoup(
        page.text, "html.parser", parse_only=SoupStrainer("script", id="__NEXT_DATA__")
    )

    script_tag = soup.find("script", id="__NEXT_DATA__")

    if script_tag is None:
        return None

    assert isinstance(script_tag, Tag)

    return script_tag


def get_next_data(imdb_session: ImdbSession, url: str) -> UntypedJson:
    script_tag = _fetch_next_data_script_tag(imdb_session.session, url)

    if script_tag is None:
        logger.log("AWS WAF token appears to have expired for {}. Requesting a new one...", url)
        imdb_session.refresh_token()
        script_tag = _fetch_next_data_script_tag(imdb_session.session, url)

    assert script_tag

    page_data = json.loads(str(script_tag.string))

    assert isinstance(page_data, dict)

    return page_data
