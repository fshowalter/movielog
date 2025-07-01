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


def _edge_title_is_not_uncredtied(edge: UntypedJson) -> bool:
    attributes: list[UntypedJson] = get_nested_value(edge, ["node", "attributes"]) or []

    return (
        len(
            {"uncredited", "voice", "scenes deleted"}.intersection(
                {attribute.get("text", "").lower() for attribute in attributes}
            )
        )
        == 0
    )


def _edge_is_valid_title_for_performer(edge: UntypedJson) -> bool:
    return edge_is_valid_title(edge) & _edge_title_is_not_uncredtied(edge)


def _build_performer(
    imdb_id: str,
    session: requests.Session,
    credits_data: UntypedJson,
) -> ImdbPerson:
    performer = ImdbPerson(imdb_id=imdb_id, credits=[])

    credit_key = "actor_credits"

    paginated_credits: UntypedJson = next(
        (
            get_nested_value(credit_group, ["credits"], {})
            for credit_group in get_nested_value(
                credits_data,
                ["data", "name", "releasedCredits"],
            )
            if credit_group["category"]["id"] == "actor"
        ),
        {},
    )

    if len(get_nested_value(paginated_credits, ["edges"], [])) == 0:
        paginated_credits = next(
            (
                get_nested_value(credit_group, ["credits"], {})
                for credit_group in get_nested_value(
                    credits_data,
                    ["data", "name", "releasedCredits"],
                )
                if credit_group["category"]["id"] == "actress"
            ),
            {},
        )
        credit_key = "actress_credits"

    performer.credits.extend(
        title_credit_for_edge(edge=edge)
        for edge in get_nested_value(paginated_credits, ["edges"], [])
        if _edge_is_valid_title_for_performer(edge)
    )

    while get_nested_value(paginated_credits, ["pageInfo", "hasNextPage"], default=False):
        query_variables = {
            "after": get_nested_value(paginated_credits, ["pageInfo", "endCursor"]),
            "id": imdb_id,
            "includeUserRating": False,
            "locale": "en-US",
        }

        query_extensions = {
            "persistedQuery": {
                "sha256Hash": "4faf04583fbf1fbc7a025e5dffc7abc3486e9a04571898a27a5a1ef59c2965f3",
                "version": 1,
            }
        }

        next_page = call_graphql(
            session=session,
            operation="NameMainFilmographyPaginatedCredits",
            variables=query_variables,
            extensions=query_extensions,
        )

        performer.credits.extend(
            title_credit_for_edge(edge=next_page_edge)
            for next_page_edge in get_nested_value(
                next_page, ["data", "name", credit_key, "edges"], []
            )
            if _edge_is_valid_title_for_performer(next_page_edge)
        )

        paginated_credits = get_nested_value(next_page, ["data", "name", credit_key])

    return performer


def get_performer(imdb_id: str) -> ImdbPerson:
    session = create_session()

    credits_data = get_credits(session=session, imdb_id=imdb_id)

    return _build_performer(imdb_id=imdb_id, session=session, credits_data=credits_data)
