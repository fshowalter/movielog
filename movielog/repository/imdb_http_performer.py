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

PEFORMER_CREDIT_CATEGORY = (
    "amzn1.imdb.concept.name_credit_category.a9ab2a8b-9153-4edb-a27a-7c2346830d77"
)


def _edge_title_role_attributes_are_valid(edge: UntypedJson) -> bool:
    attributes: list[UntypedJson] = get_nested_value(edge, ["node", "attributes"]) or []

    return (
        len(
            {"scenes deleted"}.intersection(
                {attribute.get("text", "").lower() for attribute in attributes}
            )
        )
        == 0
    )


def _edge_is_valid_title_for_performer(edge: UntypedJson) -> bool:
    return edge_is_valid_title(edge) and _edge_title_role_attributes_are_valid(edge)


def _build_performer(
    imdb_id: str,
    session: requests.Session,
    credit_groupings: list[UntypedJson],
) -> ImdbPerson:
    performer = ImdbPerson(imdb_id=imdb_id, credits=[])

    paginated_credits: UntypedJson = next(
        (
            get_nested_value(edge, ["node", "credits"], {})
            for edge in credit_groupings
            if edge["node"]["grouping"]["groupingId"] == PEFORMER_CREDIT_CATEGORY
        ),
        {},
    )

    performer.credits.extend(
        title_credit_for_edge(edge=edge)
        for edge in get_nested_value(paginated_credits, ["edges"], [])
        if _edge_is_valid_title_for_performer(edge)
    )

    has_next_page = get_nested_value(paginated_credits, ["pageInfo", "hasNextPage"])
    after = get_nested_value(paginated_credits, ["pageInfo", "endCursor"])

    while has_next_page:
        query_variables = {
            "after": after,
            "nameId": imdb_id,
            "includeUserRating": False,
            "locale": "en-US",
            "order": "DESC",
            "isProPage": False,
            "category": PEFORMER_CREDIT_CATEGORY,
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

        performer.credits.extend(
            title_credit_for_edge(edge=next_page_edge)
            for next_page_edge in get_nested_value(
                next_page_data, ["data", "name", "creditsV2", "edges"], []
            )
            if _edge_is_valid_title_for_performer(next_page_edge)
        )

        has_next_page = get_nested_value(
            next_page_data, ["data", "name", "creditsV2", "pageInfo", "hasNextPage"]
        )
        after = get_nested_value(
            next_page_data, ["data", "name", "creditsV2", "pageInfo", "endCursor"]
        )

    return performer


def get_performer(imdb_id: str) -> ImdbPerson:
    session = create_session()

    credit_groupings = get_credits(session=session, imdb_id=imdb_id)

    return _build_performer(imdb_id=imdb_id, session=session, credit_groupings=credit_groupings)
