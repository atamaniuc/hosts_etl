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

    # Создаем много хостов, чтобы вызвать логику батчинга
    # Используем маленький размер батча для тестирования
    hosts = [{"ip": f"192.168.1.{i}", "hostname": f"host{i}"} for i in range(1, 102)]

    # Mock the bulk_write result
    mock_result = Mock()
    mock_result.upserted_count = 50
    mock_result.modified_count = 0
    mock_collection.bulk_write.return_value = mock_result

    # Выполняем сохранение с указанием маленького размера батча
    storage.save(hosts, batch_size=50)

    # Должно быть 3 батча: 50 + 50 + 1 = 101 запись
    assert mock_collection.bulk_write.call_count == 3

    # Verify logging
    assert (
        mock_logger.info.call_count >= 5
    )  # Начальный лог + по одному на каждый батч + итоговый лог


@patch("storage.mongo.collection")
@patch("storage.mongo.logger")
def test_save_to_mongo_with_error(mock_logger, mock_collection):
    """Test handling of errors during saving to MongoDB"""
    storage = MongoStorage()

    # Подготавливаем данные
    hosts = [{"ip": "1.1.1.1", "hostname": "host1"}]

    # Имитируем ошибку при создании индекса
    mock_collection.create_index.side_effect = OperationFailure("Test index error")

    # Имитируем ошибку при записи
    mock_collection.bulk_write.side_effect = OperationFailure("Test bulk write error")

    # Выполняем сохранение
    storage.save(hosts)

    # Проверяем, что логи ошибок были вызваны
    mock_logger.warning.assert_called_once()
    mock_logger.error.assert_called_once()
