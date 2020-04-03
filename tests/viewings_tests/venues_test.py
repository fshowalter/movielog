import os

from pytest_mock import MockFixture

from movielog import viewings


def test_returns_venues_sorted(tmp_path: str, mocker: MockFixture) -> None:
    mocker.patch("movielog.viewings.TABLE_NAME", tmp_path)

    expected = ["Alamo Drafthouse", "Blu-ray", "DVD"]

    existing_viewings = {
        "viewing_1": "sequence: 1\ndate: 2005-03-26\nimdb_id: tt0159693\ntitle: 'Razor Blade Smile (1998)'\nvenue: DVD\n",  # noqa: 501
        "viewing_2": "sequence: 2\ndate: 2006-03-26\nimdb_id: tt0266697\ntitle: 'Kill Bill: Vol. 1 (2003)'\nvenue: Alamo Drafthouse\n",  # noqa: 501
        "viewing_3": "sequence: 2\ndate: 2007-03-26\nimdb_id: tt0053221\ntitle: 'Rio Bravo (1959)'\nvenue: Blu-ray\n",  # noqa: 501
    }

    for filename, existing_viewing in existing_viewings.items():
        with open(os.path.join(tmp_path, f"{filename}.yml"), "w") as output_file:
            output_file.write(existing_viewing)

    assert viewings.venues() == expected
