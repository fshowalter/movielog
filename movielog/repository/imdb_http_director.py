import requests

from movielog.repository.imdb_http_person import (
    ImdbPerson,
    UntypedJson,
    call_graphql,
    create_session,
    edge_is_valid_title,
    get_credits,
    title_credit_for_edge,
)
from movielog.utils.get_nested_value import get_nested_value

DIRECTOR_CREDIT_CATEGORY = (
    "amzn1.imdb.concept.name_credit_category.ace5cb4c-8708-4238-9542-04641e7c8171"
)


def _edge_is_valid_title_for_director(edge: UntypedJson) -> bool:
    return edge_is_valid_title(edge)


def _build_director(
    imdb_id: str,
    session: requests.Session,
    credit_groupings: list[UntypedJson],
) -> ImdbPerson:
    director = ImdbPerson(imdb_id=imdb_id, credits=[])

    paginated_credits: UntypedJson = next(
        (
            get_nested_value(edge, ["node", "credits"], {})
            for edge in credit_groupings
            if edge["node"]["grouping"]["groupingId"] == DIRECTOR_CREDIT_CATEGORY
        ),
        {},
    )

    director.credits.extend(
        title_credit_for_edge(edge=edge)
        for edge in get_nested_value(paginated_credits, ["edges"], [])
        if _edge_is_valid_title_for_director(edge)
    )

    if get_nested_value(paginated_credits, ["pageInfo", "hasNextPage"]):
        query_variables = {
            "after": get_nested_value(paginated_credits, ["pageInfo", "endCursor"]),
            "nameId": imdb_id,
            "includeUserRating": False,
            "locale": "en-US",
            "order": "DESC",
            "isProPage": False,
            "category": DIRECTOR_CREDIT_CATEGORY,
        }

        query_extensions = {
            "persistedQuery": {
                "sha256Hash": "096f555fe586eed2dde6c19293bd623a102b64cc2abc9f1ab6ef0a12b1cd36ec",
                "version": 1,
            }
        }

        next_page_data = call_graphql(
            session=session,
            operation="FilmographyV2Pagination",
            variables=query_variables,
            extensions=query_extensions,
        )

        director.credits.extend(
            title_credit_for_edge(edge=next_page_edge)
            for next_page_edge in get_nested_value(
                next_page_data, ["data", "name", "creditsV2", "edges"], []
            )
            if _edge_is_valid_title_for_director(next_page_edge)
        )

    return director


def get_director(imdb_id: str) -> ImdbPerson:
    session = create_session()

    credit_groupings = get_credits(session=session, imdb_id=imdb_id)

    return _build_director(imdb_id=imdb_id, session=session, credit_groupings=credit_groupings)
