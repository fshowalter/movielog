from typing import Callable

import yaml

from movielog.watchlist_file import Title, WatchlistFile


def test_returns_watchlist_file_from_yaml(
    build_watchlist_file: Callable[..., WatchlistFile]
) -> None:
    titles = [
        Title(imdb_id="tt0083190", title="Thief", year=1981),
        Title(imdb_id="tt0085780", title="The Keep", year=1983),
        Title(imdb_id="tt0091474", title="Manhunter", year=1986),
    ]

    file_path = "test/path/object.yml"

    expected = build_watchlist_file(
        name="Michael Mann",
        imdb_id="nm0000520",
        frozen=False,
        titles=titles,
        file_path=file_path,
    )

    yaml_string = """
      frozen: false
      name: Michael Mann
      imdb_id: nm0000520
      titles:
      - title: Thief
        imdb_id: tt0083190
        year: 1981
      - title: The Keep
        imdb_id: tt0085780
        year: 1983
      - title: Manhunter
        imdb_id: tt0091474
        year: 1986
    """

    yaml_object = yaml.safe_load(yaml_string)

    assert (
        expected.__class__.from_yaml_object(
            yaml_object=yaml_object, file_path=file_path
        )
        == expected
    )
