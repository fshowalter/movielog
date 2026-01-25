import requests

from movielog.repository.imdb_http_person import (
    ImdbPerson,
    UntypedJson,
    call_graphql,
    edge_is_valid_title,
    get_credits,
    title_credit_for_edge,
)
from movielog.utils.get_nested_value import get_nested_value

WRITER_CREDIT_CATEGORY = (
    "amzn1.imdb.concept.name_credit_category.c84ecaff-add5-4f2e-81db-102a41881fe3"
)


def _edge_is_valid_title_for_writer(edge: UntypedJson) -> bool:
    return edge_is_valid_title(edge)


def _build_writer(
    imdb_id: str,
    session: requests.Session,
    credit_groupings: list[UntypedJson],
) -> ImdbPerson:
    writer = ImdbPerson(imdb_id=imdb_id, credits=[])

    paginated_credits: UntypedJson = next(
        (
            get_nested_value(edge, ["node", "credits"], {})
            for edge in credit_groupings
            if edge["node"]["grouping"]["groupingId"] == WRITER_CREDIT_CATEGORY
        ),
        {},
    )

    writer.credits.extend(
        title_credit_for_edge(edge=edge)
        for edge in get_nested_value(paginated_credits, ["edges"], [])
        if _edge_is_valid_title_for_writer(edge)
    )

    if get_nested_value(paginated_credits, ["pageInfo", "hasNextPage"]):
        query_variables = {
            "after": get_nested_value(paginated_credits, ["pageInfo", "endCursor"]),
            "nameId": imdb_id,
            "includeUserRating": False,
            "locale": "en-US",
            "order": "DESC",
            "isProPage": False,
            "category": WRITER_CREDIT_CATEGORY,
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

        writer.credits.extend(
            title_credit_for_edge(edge=next_page_edge)
            for next_page_edge in get_nested_value(
                next_page_data, ["data", "name", "creditsV2", "edges"], []
            )
            if _edge_is_valid_title_for_writer(next_page_edge)
        )

    return writer


def get_writer(session: requests.Session, imdb_id: str) -> ImdbPerson:
    credit_groupings = get_credits(session=session, imdb_id=imdb_id)

    return _build_writer(imdb_id=imdb_id, session=session, credit_groupings=credit_groupings)
