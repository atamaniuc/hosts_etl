from unittest.mock import patch
from storage.mongo import MongoStorage


@patch("storage.mongo.collection")
@patch("storage.mongo.logger")
def test_save_empty_data(mock_logger, mock_collection):
    """Test saving empty data to MongoDB"""
    storage = MongoStorage()

    # Call save with empty data
    storage.save([])

    # Verify that the appropriate log was called and no database operations were performed
    mock_logger.info.assert_called_with("📭 No data to save")
    mock_collection.bulk_write.assert_not_called()
