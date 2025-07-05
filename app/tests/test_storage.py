from unittest.mock import patch, Mock
from storage.mongo import MongoStorage


@patch("storage.mongo.collection")
def test_save_to_mongo(mock_collection):
    storage = MongoStorage()

    # Mock the update_one result
    mock_result = Mock()
    mock_result.modified_count = 1
    mock_result.upserted_id = None
    mock_collection.update_one.return_value = mock_result

    storage.save([{"ip": "1.1.1.1", "hostname": "h"}])

    # Verify that update_one was called
    mock_collection.update_one.assert_called_once()
