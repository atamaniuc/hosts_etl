from unittest.mock import patch
from processors.deduplicate import DeduplicationProcessor

# import pydevd_pycharm


def test_deduplication():
    hosts = [
        {"ip": "1.1.1.1", "hostname": "host"},
        {"ip": "1.1.1.1", "hostname": "host"},
    ]
    processor = DeduplicationProcessor()
    result = processor.process(hosts)
    assert len(result) == 1


def test_deduplication_ip_hostname():
    hosts = [
        {"ip": "1.1.1.1", "hostname": "host"},
        {"ip": "1.1.1.1", "hostname": "host"},
        {"ip": "1.1.1.1", "hostname": "host2"},
        {"ip": "2.2.2.2", "hostname": "host"},
    ]
    processor = DeduplicationProcessor()
    result = processor.process(hosts)
    assert len(result) == 3


def test_deduplication_only_ip():
    # pydevd_pycharm.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)
    hosts = [
        {"ip": "1.1.1.1"},
        {"ip": "1.1.1.1"},
        {"ip": "2.2.2.2"},
    ]
    processor = DeduplicationProcessor()
    result = processor.process(hosts)
    assert len(result) == 2


def test_deduplication_only_hostname():
    # pydevd_pycharm.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)
    hosts = [
        {"hostname": "host1"},
        {"hostname": "host1"},
        {"hostname": "host2"},
    ]
    processor = DeduplicationProcessor()
    result = processor.process(hosts)
    assert len(result) == 2


def test_deduplication_no_ip_hostname():
    hosts = [
        {"source": "qualys", "os": "linux"},
        {"source": "qualys", "os": "linux"},
        {"source": "crowdstrike", "os": "windows"},
    ]
    processor = DeduplicationProcessor()
    result = processor.process(hosts)
    assert len(result) == 3


@patch("processors.deduplicate.logger")
def test_deduplication_empty_data(mock_logger):
    """Test deduplication with empty data (to cover the 'if not data' branch)"""
    processor = DeduplicationProcessor()
    result = processor.process([])

    # Проверяем, что результат пуст
    assert result == []

    # Проверяем, что был вызван соответствующий лог
    mock_logger.info.assert_called_with("📭 No data to deduplicate")
