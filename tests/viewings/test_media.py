from datetime import date, timedelta

from movielog.viewings import api as viewings_api
from movielog.viewings import media


def test_recent_medai_returns_recent_media(tmp_path: str) -> None:

    expected = ["Blu-ray", "Criterion Channel"]

    viewings_api.create(
        viewing_date=date(2005, 3, 26),
        imdb_id="tt0159693",
        medium="DVD",
        slug="razor-blade-smile-1998",
    )

    viewings_api.create(
        viewing_date=date(2006, 4, 29),
        imdb_id="tt0025480",
        medium="Arte",
        slug="bad-seed-1934",
    )

    viewings_api.create(
        viewing_date=(date.today() - timedelta(days=1)),
        imdb_id="tt0266697",
        medium="Criterion Channel",
        slug="kill-bill-vol-1-2003",
    )

    viewings_api.create(
        viewing_date=date.today(),
        imdb_id="tt0053221",
        medium="Blu-ray",
        slug="rio-bravo-1959",
    )

    assert expected == media.recent()
