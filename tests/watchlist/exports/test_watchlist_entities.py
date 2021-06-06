import datetime
import json
import os

import pytest

from movielog.moviedata.core import movies_table, people_table
from movielog.reviews import reviews_table
from movielog.watchlist import watchlist_table
from movielog.watchlist.exports import watchlist_entities


@pytest.fixture(autouse=True)
def init_db() -> None:
    movies_table.reload(
        [
            movies_table.Row(
                imdb_id="tt0038355",
                title="The Big Sleep",
                original_title="The Big Sleep",
                year=1946,
                runtime_minutes=115,
                principal_cast_ids="",
            ),
            movies_table.Row(
                imdb_id="tt0053221",
                title="Rio Bravo",
                original_title="Original Rio Bravo",
                year=1959,
                runtime_minutes=141,
                principal_cast_ids="",
            ),
            movies_table.Row(
                imdb_id="tt0190590",
                title="O Brother, Where Art Thou?",
                original_title="Original Rio Bravo",
                year=2000,
                runtime_minutes=121,
                principal_cast_ids="",
            ),
            movies_table.Row(
                imdb_id="tt0055928",
                title="Dr. No",
                original_title="Dr. No",
                year=1962,
                runtime_minutes=111,
                principal_cast_ids="",
            ),
        ]
    )

    people_table.reload(
        [
            people_table.Row(
                imdb_id="nm0001328",
                full_name="Howard Hawks",
                known_for_title_ids="",
            ),
            people_table.Row(
                imdb_id="nm0000078",
                full_name="John Wayne",
                known_for_title_ids="",
            ),
            people_table.Row(
                imdb_id="nm0001509",
                full_name="Dean Martin",
                known_for_title_ids="",
            ),
            people_table.Row(
                imdb_id="nm0001054",
                full_name="Joel Cohen",
                known_for_title_ids="",
            ),
            people_table.Row(
                imdb_id="nm0001053",
                full_name="Ethan Cohen",
                known_for_title_ids="",
            ),
            people_table.Row(
                imdb_id="nm0102824",
                full_name="Leigh Brackett",
                known_for_title_ids="",
            ),
        ]
    )

    reviews_table.reload(
        [
            reviews_table.Row(
                movie_imdb_id="tt0053221",
                date=datetime.date(2021, 1, 29),
                sequence=165,
                grade="A+",
                grade_value=5.33,
                slug="rio-bravo-1959",
                venue="Blu-ray",
            )
        ]
    )

    watchlist_table.reload(
        [
            watchlist_table.Row(
                movie_imdb_id="tt0053221",
                director_imdb_id="nm0001328",
                slug="howard-hawks",
                performer_imdb_id=None,
                writer_imdb_id=None,
                collection_name=None,
            ),
            watchlist_table.Row(
                movie_imdb_id="tt0038355",
                director_imdb_id="nm0001328",
                slug="howard-hawks",
                performer_imdb_id=None,
                writer_imdb_id=None,
                collection_name=None,
            ),
            watchlist_table.Row(
                movie_imdb_id="tt0190590",
                director_imdb_id="nm0001054",
                slug="the-coen-brothers",
                performer_imdb_id=None,
                writer_imdb_id=None,
                collection_name=None,
            ),
            watchlist_table.Row(
                movie_imdb_id="tt0053221",
                director_imdb_id=None,
                slug="john-wayne",
                performer_imdb_id="nm0000078",
                writer_imdb_id=None,
                collection_name=None,
            ),
            watchlist_table.Row(
                movie_imdb_id="tt0053221",
                director_imdb_id=None,
                slug="dean-martin",
                performer_imdb_id="nm0001509",
                writer_imdb_id=None,
                collection_name=None,
            ),
            watchlist_table.Row(
                movie_imdb_id="tt0053221",
                director_imdb_id=None,
                slug="leigh-brackett",
                performer_imdb_id=None,
                writer_imdb_id="nm0102824",
                collection_name=None,
            ),
            watchlist_table.Row(
                movie_imdb_id="tt0038355",
                director_imdb_id=None,
                slug="leigh-brackett",
                performer_imdb_id=None,
                writer_imdb_id="nm0102824",
                collection_name=None,
            ),
            watchlist_table.Row(
                movie_imdb_id="tt0055928",
                director_imdb_id=None,
                slug="bond",
                performer_imdb_id=None,
                writer_imdb_id=None,
                collection_name="Bond",
            ),
        ]
    )


def test_exports_watchlist_entities(tmp_path: str) -> None:
    expected = [
        {
            "imdb_id": "nm0001328",
            "name": "Howard Hawks",
            "slug": "howard-hawks",
            "title_count": 2,
            "review_count": 1,
            "entity_type": "director",
        },
        {
            "imdb_id": "nm0001054",
            "name": "The Coen Brothers",
            "slug": "the-coen-brothers",
            "title_count": 1,
            "review_count": 0,
            "entity_type": "director",
        },
        {
            "imdb_id": "nm0001509",
            "name": "Dean Martin",
            "slug": "dean-martin",
            "title_count": 1,
            "review_count": 1,
            "entity_type": "performer",
        },
        {
            "imdb_id": "nm0000078",
            "name": "John Wayne",
            "slug": "john-wayne",
            "title_count": 1,
            "review_count": 1,
            "entity_type": "performer",
        },
        {
            "imdb_id": "nm0102824",
            "name": "Leigh Brackett",
            "slug": "leigh-brackett",
            "title_count": 2,
            "review_count": 1,
            "entity_type": "writer",
        },
        {
            "name": "Bond",
            "slug": "bond",
            "title_count": 1,
            "review_count": 0,
            "entity_type": "collection",
        },
    ]

    watchlist_entities.export()

    with open(os.path.join(tmp_path, "watchlist_entities.json"), "r") as output_file:
        file_content = json.load(output_file)

    assert file_content == expected
