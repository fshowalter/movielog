from movielog.watchlist_file import Title
import yaml


def test_returns_title_from_yaml() -> None:
    expected = Title(title="Rio Bravo", imdb_id="tt0053221", year=1959,)

    yaml_string = """
      imdb_id: tt0053221
      title: Rio Bravo
      year: 1959
    """

    yaml_object = yaml.safe_load(yaml_string)

    assert Title.from_yaml_object(yaml_object) == expected


def test_if_notes_adds_notes() -> None:
    expected = Title(
        title="Rio Bravo", imdb_id="tt0053221", year=1959, notes="Best. Movie. Ever."
    )

    yaml_string = """
      imdb_id: tt0053221
      title: Rio Bravo
      year: 1959
      notes: Best. Movie. Ever.
    """

    yaml_object = yaml.safe_load(yaml_string)

    assert Title.from_yaml_object(yaml_object) == expected
