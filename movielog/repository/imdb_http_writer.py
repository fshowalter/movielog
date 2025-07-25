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

TIMEOUT = 30


def _edge_title_job_is_valid(edge: UntypedJson) -> bool:
    jobs: list[UntypedJson] = get_nested_value(edge, ["node", "jobs"]) or []

    return all("original material" not in job.get("text", "").lower() for job in jobs)


def _edge_title_is_not_uncredtied(edge: UntypedJson) -> bool:
    attributes: list[UntypedJson] = get_nested_value(edge, ["node", "attributes"]) or []

    return all("uncredited" not in attribute.get("text", "").lower() for attribute in attributes)


def _edge_is_valid_title_for_writer(edge: UntypedJson) -> bool:
    return (
        edge_is_valid_title(edge)
        & _edge_title_is_not_uncredtied(edge)
        & _edge_title_job_is_valid(edge)
    )


def _build_writer(
    imdb_id: str,
    session: requests.Session,
    credits_data: UntypedJson,
) -> ImdbPerson:
    writer = ImdbPerson(imdb_id=imdb_id, credits=[])

    paginated_credits: UntypedJson = next(
        (
            get_nested_value(credit_group, ["credits"], {})
            for credit_group in get_nested_value(
                credits_data,
                ["data", "name", "releasedCredits"],
            )
            if credit_group["category"]["id"] == "writer"
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
            "id": imdb_id,
            "includeUserRating": False,
            "locale": "en-US",
        }

        query_extensions = {
            "persistedQuery": {
                "sha256Hash": "f01a9a65c7afc1b50f49764610257d436cf6359e48c08de26c078da0d438d0e9",
                "version": 1,
            }
        }

        next_page_data = call_graphql(
            session=session,
            operation="NameMainFilmographyPaginatedCredits",
            variables=query_variables,
            extensions=query_extensions,
        )

        writer.credits.extend(
            title_credit_for_edge(edge=next_page_edge)
            for next_page_edge in get_nested_value(
                next_page_data, ["data", "name", "writer_credits", "edges"], []
            )
            if _edge_is_valid_title_for_writer(next_page_edge)
        )

    return writer


def get_writer(imdb_id: str) -> ImdbPerson:
    session = create_session()

    credits_data = get_credits(session=session, imdb_id=imdb_id)

    return _build_writer(imdb_id=imdb_id, session=session, credits_data=credits_data)
