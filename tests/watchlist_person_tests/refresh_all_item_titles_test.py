from typing import Type, Union

import pytest
from pytest_mock import MockerFixture

from movielog.watchlist_person import Director, Performer, Writer


@pytest.mark.parametrize(
    "class_type",
    [Director, Performer, Writer],
)
def test_calls_refresh_item_titles_on_all_unfrozen_items(
    mocker: MockerFixture,
    class_type: Type[Union[Performer, Director, Writer]],
) -> None:
    person = class_type(file_path=None, name="Alfred Hitchcock", imdb_id="nm0000033")
    refresh_item_titles_mock = mocker.patch.object(person, "refresh_item_titles")

    mocker.patch.object(class_type, "unfrozen_items", return_value=[person])

    class_type.refresh_all_item_titles()

    refresh_item_titles_mock.assert_called_once()
