
from pytest_mock import MockFixture

from movielog import watchlist


def test_add_collection_saves_created_collection(mocker: MockFixture) -> None:
    mock = mocker.patch('movielog.watchlist.Collection.new', autospec=True)
    mock_return = mocker.MagicMock(watchlist.Collection)

    mock.return_value = mock_return

    new_collection = watchlist.add_collection('test collection name')

    assert new_collection == mock_return

    mock_return.save.assert_called()


def test_update_collection_saves_updated_collection(mocker: MockFixture) -> None:
    mock_collection = mocker.MagicMock(watchlist.Collection)

    watchlist.update_collection(mock_collection)

    mock_collection.save.assert_called()
