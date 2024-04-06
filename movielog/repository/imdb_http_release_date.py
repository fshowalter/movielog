import json
from datetime import datetime
from typing import Optional, TypedDict, cast

import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag
from requests.adapters import HTTPAdapter, Retry

TIMEOUT = 30

TextType = TypedDict(
    "TextType",
    {
        "text": str,
        "subText": str,
    },
)

ContentCategorySectionItem = TypedDict(
    "ContentCategorySectionItem",
    {
        "id": str,
        "rowTitle": str,
        "listContent": list[TextType],
    },
)

ContentCategorySection = TypedDict(
    "ContentCategorySection", {"items": list[ContentCategorySectionItem]}
)

ContentCategory = TypedDict(
    "ContentCategory", {"id": str, "section": ContentCategorySection}
)

ContentData = TypedDict(
    "ContentData",
    {
        "categories": list[ContentCategory],
    },
)


PageProps = TypedDict(
    "PageProps",
    {
        "contentData": ContentData,
    },
)

Props = TypedDict("Props", {"pageProps": PageProps})

PageData = TypedDict(
    "PageData",
    {"props": Props},
)


def unknown_date(release_year: str) -> str:
    return "{0}-??-??".format(release_year or "????")


def get_release_date_page_data(imdb_id: str) -> PageData:
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])

    session.mount("https://", HTTPAdapter(max_retries=retries))

    page = session.get(
        "https://www.imdb.com/title/{0}/releaseinfo".format(imdb_id),
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

    return cast(PageData, json.loads(str(script_tag.string)))


def parse_first_release_date(page_data: PageData) -> Optional[str]:
    releases = next(
        (
            category
            for category in page_data["props"]["pageProps"]["contentData"]["categories"]
            if category["id"] == "releases"
        ),
        None,
    )

    if not releases or not releases["section"]["items"]:
        return None

    release_date = releases["section"]["items"][0]

    if not release_date:
        return None

    if not release_date["listContent"][0]:
        return None

    return release_date["listContent"][0]["text"]


def get_release_date(imdb_id: str, release_year: str) -> str:
    page_data = get_release_date_page_data(imdb_id=imdb_id)

    first_release_date = parse_first_release_date(page_data=page_data)

    if not first_release_date:
        return unknown_date(release_year)

    try:
        return datetime.strptime(first_release_date, "%B %d, %Y").date().isoformat()
    except ValueError:
        try:  # noqa: WPS505
            return datetime.strptime(first_release_date, "%B %Y").date().isoformat()
        except ValueError:
            return unknown_date(release_year)
