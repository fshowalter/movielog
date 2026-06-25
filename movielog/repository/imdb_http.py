import requests
from requests.adapters import HTTPAdapter, Retry

TIMEOUT = 30

Session = requests.Session


def create_session(token: str) -> requests.Session:
    session = requests.Session()

    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])

    session.mount("https://", HTTPAdapter(max_retries=retries))

    if token:
        session.cookies["aws-waf-token"] = token

    return session


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
