from unittest.mock import patch, Mock
from pymongo.errors import OperationFailure
from storage.mongo import MongoStorage


@patch("storage.mongo.collection")
@patch("storage.mongo.logger")
def test_save_to_mongo(mock_logger, mock_collection):
    storage = MongoStorage()

    # Mock the bulk_write result
    mock_result = Mock()
    mock_result.upserted_count = 1
    mock_result.modified_count = 0
    mock_collection.bulk_write.return_value = mock_result

    storage.save([{"ip": "1.1.1.1", "hostname": "h"}])

    # Verify that bulk_write was called
    mock_collection.bulk_write.assert_called_once()

    # Verify logging
    mock_logger.info.assert_called()


@patch("storage.mongo.collection")
@patch("storage.mongo.logger")
def test_save_to_mongo_with_batch(mock_logger, mock_collection):
    """Test save with batching (for coverage of the batch processing logic)"""
    storage = MongoStorage()

    # Create many hosts to trigger batching logic
    # Use small batch size for testing
    hosts = [{"ip": f"192.168.1.{i}", "hostname": f"host{i}"} for i in range(1, 102)]

    # Mock the bulk_write result
    mock_result = Mock()
    mock_result.upserted_count = 50
    mock_result.modified_count = 0
    mock_collection.bulk_write.return_value = mock_result

    # Execute save with specified small batch size
    storage.save(hosts, batch_size=50)

    # Should be 3 batches: 50 + 50 + 1 = 101 records
    assert mock_collection.bulk_write.call_count == 3

    # Verify logging
    assert mock_logger.info.call_count >= 5  # Initial log + one per batch + final log


@patch("storage.mongo.collection")
@patch("storage.mongo.logger")
def test_save_to_mongo_with_error(mock_logger, mock_collection):
    """Test handling of errors during saving to MongoDB"""
    storage = MongoStorage()

    # Prepare test data
    hosts = [{"ip": "1.1.1.1", "hostname": "host1"}]

    # Simulate error during index creation
    mock_collection.create_index.side_effect = OperationFailure("Test index error")

    # Simulate error during bulk write
    mock_collection.bulk_write.side_effect = OperationFailure("Test bulk write error")

    # Execute save operation
    storage.save(hosts)

    # Check that error logs were called
    mock_logger.warning.assert_called_once()
    mock_logger.error.assert_called_once()
