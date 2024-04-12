from typing import Literal, Optional, TypedDict

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils.logging import logger

JsonTitle = TypedDict(
    "JsonTitle",
    {
        "imdbId": str,
        "title": str,
        "year": str,
        "sortTitle": str,
        "slug": Optional[str],
        "grade": Optional[str],
        "gradeValue": Optional[int],
        "releaseSequence": str,
        "reviewDate": Optional[str],
        "viewingSequence": Optional[str],
    },
)

JsonCredits = TypedDict(
    "JsonCredits",
    {
        "titles": list[JsonTitle],
        "reviewCount": int,
        "watchlistCount": int,
    },
)


JsonNameIntermediate = TypedDict(
    "JsonNameIntermediate",
    {
        "slug": str,
        "name": str,
        "director": JsonCredits,
        "director_title_ids": set[str],
        "performer": JsonCredits,
        "performer_title_ids": set[str],
        "writer": JsonCredits,
        "writer_title_ids": set[str],
    },
)

JsonNameFinal = TypedDict(
    "JsonNameFinal",
    {
        "slug": str,
        "name": str,
        "director": JsonCredits,
        "performer": JsonCredits,
        "writer": JsonCredits,
        "mostCreditedAs": Literal["director", "performer", "writer"],
    },
)


CastAndCrewByImdbId = dict[frozenset[str], JsonNameIntermediate]


def populate_watchlist_data(
    cast_and_crew_by_imdb_id: CastAndCrewByImdbId, repository_data: RepositoryData
) -> None:
    for director in repository_data.watchlist_people["directors"]:
        if isinstance(director.imdb_id, list):
            key = frozenset(director.imdb_id)
        else:
            key = frozenset((director.imdb_id,))
        cast_and_crew_by_imdb_id[key]["director_title_ids"].update(director.title_ids)

    for performer in repository_data.watchlist_people["performers"]:
        if isinstance(performer.imdb_id, list):
            key = frozenset(performer.imdb_id)
        else:
            key = frozenset((performer.imdb_id,))
        cast_and_crew_by_imdb_id[key]["performer_title_ids"].update(performer.title_ids)

    for writer in repository_data.watchlist_people["writers"]:
        if isinstance(writer.imdb_id, list):
            key = frozenset(writer.imdb_id)
        else:
            key = frozenset((writer.imdb_id,))
        cast_and_crew_by_imdb_id[key]["writer_title_ids"].update(writer.title_ids)


def intialize_cast_and_crew_by_imdb_id(
    repository_data: RepositoryData,
) -> CastAndCrewByImdbId:
    cast_and_crew_by_imdb_id: CastAndCrewByImdbId = {}

    for name in repository_data.names:
        if isinstance(name.imdb_id, list):
            key = frozenset(name.imdb_id)
        else:
            key = frozenset((name.imdb_id,))

        cast_and_crew_by_imdb_id[key] = JsonNameIntermediate(
            name=name.name,
            slug=name.slug,
            director=JsonCredits(titles=[], reviewCount=0, watchlistCount=0),
            writer=JsonCredits(titles=[], reviewCount=0, watchlistCount=0),
            performer=JsonCredits(titles=[], reviewCount=0, watchlistCount=0),
            director_title_ids=set(),
            writer_title_ids=set(),
            performer_title_ids=set(),
        )

    return cast_and_crew_by_imdb_id


def check_title_for_names(
    title: repository_api.Title,
    cast_and_crew_by_imdb_id: CastAndCrewByImdbId,
) -> None:
    director_ids = frozenset((director.imdb_id for director in title.directors))

    performer_ids = frozenset((performer.imdb_id for performer in title.performers))

    writer_ids = frozenset((writer.imdb_id for writer in title.writers))

    for name_key, name_value in cast_and_crew_by_imdb_id.items():
        if name_key & director_ids:
            name_value["director_title_ids"].add(title.imdb_id)
        if name_key & performer_ids:
            name_value["performer_title_ids"].add(title.imdb_id)
        if name_key & writer_ids:
            name_value["writer_title_ids"].add(title.imdb_id)


def add_watchlist_credits(  # noqa: WPS210
    cast_and_crew_by_imdb_id: CastAndCrewByImdbId, repository_data: RepositoryData
) -> None:
    for watchlist_person_kind in repository_api.WATCHLIST_PERSON_KINDS:
        for watchlist_person in repository_data.watchlist_people[watchlist_person_kind]:
            for title_id in watchlist_person.title_ids:
                title = repository_data.titles[title_id]
                check_title_for_names(title, cast_and_crew_by_imdb_id)


def add_review_credits(
    cast_and_crew_by_imdb_id: CastAndCrewByImdbId, repository_data: RepositoryData
) -> None:
    for reviewed_title in repository_data.reviewed_titles:
        check_title_for_names(reviewed_title, cast_and_crew_by_imdb_id)


def build_json_title(title_id: str, repository_data: RepositoryData) -> JsonTitle:
    title = repository_data.titles[title_id]
    review = repository_data.reviews.get(title_id, None)
    viewings = sorted(
        (
            viewing
            for viewing in repository_data.viewings
            if viewing.imdb_id == title_id
        ),
        key=lambda title_viewing: title_viewing.sequence,
    )

    return JsonTitle(
        imdbId=title.imdb_id,
        title=title.title,
        year=title.year,
        slug=review.slug if review else None,
        grade=review.grade if review else None,
        sortTitle=title.sort_title,
        gradeValue=review.grade_value if review else None,
        releaseSequence=title.release_sequence,
        reviewDate=review.date.isoformat() if review else None,
        viewingSequence=(
            "{0}-{1}".format(review.date.isoformat(), viewings[0].sequence)
            if viewings and review
            else None
        ),
    )


def populate_title_data(
    cast_and_crew_by_imdb_id: CastAndCrewByImdbId, repository_data: RepositoryData
) -> None:
    for _name_key, name_value in cast_and_crew_by_imdb_id.items():
        for director_title_id in name_value["director_title_ids"]:
            name_value["director"]["titles"].append(
                build_json_title(director_title_id, repository_data)
            )
        name_value["director"]["titles"].sort(
            key=lambda title: title["releaseSequence"]
        )

        for performer_title_id in name_value["performer_title_ids"]:
            name_value["performer"]["titles"].append(
                build_json_title(performer_title_id, repository_data)
            )

        name_value["performer"]["titles"].sort(
            key=lambda title: title["releaseSequence"]
        )

        for writer_title_id in name_value["writer_title_ids"]:
            name_value["writer"]["titles"].append(
                build_json_title(writer_title_id, repository_data)
            )

        name_value["writer"]["titles"].sort(key=lambda title: title["releaseSequence"])


def populate_counts(
    cast_and_crew_by_imdb_id: CastAndCrewByImdbId, repository_data: RepositoryData
) -> None:
    for _name_key, name_value in cast_and_crew_by_imdb_id.items():
        name_value["director"]["reviewCount"] = len(
            repository_data.reviews.keys() & name_value["director_title_ids"]
        )
        name_value["director"]["watchlistCount"] = len(
            name_value["director_title_ids"] - repository_data.reviews.keys()
        )

        name_value["performer"]["reviewCount"] = len(
            repository_data.reviews.keys() & name_value["performer_title_ids"]
        )
        name_value["performer"]["watchlistCount"] = len(
            name_value["performer_title_ids"] - repository_data.reviews.keys()
        )

        name_value["writer"]["reviewCount"] = len(
            repository_data.reviews.keys() & name_value["writer_title_ids"]
        )
        name_value["writer"]["watchlistCount"] = len(
            name_value["writer_title_ids"] - repository_data.reviews.keys()
        )


def transform_to_final(intermediate_name: JsonNameIntermediate) -> JsonNameFinal:
    most_credited_as: Optional[Literal["director", "performer", "writer"]] = None

    director_titles = (
        intermediate_name["director"]["reviewCount"]
        + intermediate_name["director"]["watchlistCount"]
    )
    performer_titles = (
        intermediate_name["performer"]["reviewCount"]
        + intermediate_name["performer"]["watchlistCount"]
    )
    writer_titles = (
        intermediate_name["writer"]["reviewCount"]
        + intermediate_name["writer"]["watchlistCount"]
    )

    if (director_titles >= performer_titles) and (director_titles >= writer_titles):
        most_credited_as = "director"
    elif (performer_titles >= director_titles) and (performer_titles >= writer_titles):
        most_credited_as = "performer"
    else:
        most_credited_as = "writer"

    return JsonNameFinal(
        name=intermediate_name["name"],
        slug=intermediate_name["slug"],
        director=intermediate_name["director"],
        writer=intermediate_name["writer"],
        performer=intermediate_name["performer"],
        mostCreditedAs=most_credited_as,
    )


def name_has_reviews(name: JsonNameIntermediate) -> bool:
    for credits in (name["director"], name["performer"], name["writer"]):
        if credits["reviewCount"] > 0:
            return True

    return False


def build_cast_and_crew(
    repository_data: RepositoryData,
) -> list[JsonNameFinal]:
    cast_and_crew_by_imdb_id = intialize_cast_and_crew_by_imdb_id(repository_data)

    add_watchlist_credits(cast_and_crew_by_imdb_id, repository_data)
    add_review_credits(cast_and_crew_by_imdb_id, repository_data)
    populate_title_data(cast_and_crew_by_imdb_id, repository_data)
    populate_counts(cast_and_crew_by_imdb_id, repository_data)

    return [
        transform_to_final(name_value)
        for (_imdb_id, name_value) in cast_and_crew_by_imdb_id.items()
        if name_has_reviews(name_value)
    ]


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "cast-and-crew")

    cast_and_crew = build_cast_and_crew(repository_data=repository_data)

    exporter.serialize_dicts_to_folder(
        sorted(cast_and_crew, key=lambda name: name["slug"]),
        "cast-and-crew",
        filename_key=lambda name: name["slug"],
    )
