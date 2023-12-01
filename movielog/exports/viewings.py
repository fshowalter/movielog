from typing import Optional, TypedDict

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.utils.logging import logger

JsonViewing = TypedDict(
    "JsonViewing",
    {
        "sequence": int,
        "viewingYear": str,
        "viewingDate": str,
        "releaseDate": str,
        "title": str,
        "sortTitle": str,
        "medium": Optional[str],
        "venue": Optional[str],
        "year": str,
        "slug": str,
        "genres": list[str],
    },
)


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "unreviewed-works")

    json_unreviewed_works = [
        JsonUnreviewedWork(
            slug=work.slug,
            title=work.title,
            subtitle=work.subtitle,
            sortTitle=work.sort_title,
            yearPublished=work.year,
            kind=work.kind,
            authors=[
                json_work_author.build_json_work_author(
                    work_author=work_author, all_authors=repository_data.authors
                )
                for work_author in work.work_authors
            ],
            includedInSlugs=[
                included_in_work.slug
                for included_in_work in work.included_in_works(repository_data.works)
            ],
        )
        for work in repository_data.works
        if not work.review(repository_data.reviews)
    ]

    exporter.serialize_dicts_to_folder(
        json_unreviewed_works,
        "unreviewed_works",
        filename_key=lambda work: work["slug"],
    )
