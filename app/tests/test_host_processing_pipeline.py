from unittest.mock import MagicMock, patch
import pytest
from pipeline.config import PipelineConfig
from pipeline.host_processing_pipeline import HostProcessingPipeline


@pytest.fixture
def mock_config():
    """Create a mock configuration with all necessary components."""
    config = MagicMock(spec=PipelineConfig)

    # Mock fetchers
    fetcher1 = MagicMock()
    fetcher1.fetch.return_value = [
        {"hostname": "host1", "ip": "192.168.1.1", "source": "source1"}
    ]
    fetcher1.__str__.return_value = "MockFetcher1"

    fetcher2 = MagicMock()
    fetcher2.fetch.return_value = [
        {"hostname": "host2", "ip": "192.168.1.2", "source": "source2"}
    ]
    fetcher2.__str__.return_value = "MockFetcher2"

    config.fetchers = [fetcher1, fetcher2]

    # Mock normalizer, deduplicator, storage, and visualizer
    config.normalizer = MagicMock()
    config.normalizer.process.return_value = [
        {"hostname": "host1", "ip": "192.168.1.1", "source": "source1", "os": "Linux"},
        {
            "hostname": "host2",
            "ip": "192.168.1.2",
            "source": "source2",
            "os": "Windows",
        },
    ]

    config.deduplicator = MagicMock()
    config.deduplicator.process.return_value = [
        {"hostname": "host1", "ip": "192.168.1.1", "source": "source1", "os": "Linux"},
        {
            "hostname": "host2",
            "ip": "192.168.1.2",
            "source": "source2",
            "os": "Windows",
        },
    ]

    config.storage = MagicMock()
    config.visualizer = MagicMock()
    config.visualizer.generate.return_value = {
        "total_hosts": 2,
        "by_source": {"source1": 1, "source2": 1},
        "by_os": {"Linux": 1, "Windows": 1},
    }

    return config


def test_host_processing_pipeline_init(mock_config):
    """Test pipeline initialization with configuration."""
    pipeline = HostProcessingPipeline(mock_config)

    assert pipeline.fetchers == mock_config.fetchers
    assert pipeline.normalizer == mock_config.normalizer
    assert pipeline.deduplicator == mock_config.deduplicator
    assert pipeline.storage == mock_config.storage
    assert pipeline.visualizer == mock_config.visualizer


@patch("pipeline.host_processing_pipeline.logger")
def test_extract_method(mock_logger, mock_config):
    """Test the _extract method that fetches data from multiple sources."""
    pipeline = HostProcessingPipeline(mock_config)

    # Call _extract method
    result = pipeline._extract()

    # Check that fetchers were called
    mock_config.fetchers[0].fetch.assert_called_once()
    mock_config.fetchers[1].fetch.assert_called_once()

    # Check that we got the combined results
    assert len(result) == 2
    assert result[0]["hostname"] == "host1"
    assert result[1]["hostname"] == "host2"

    # Check that logging happened
    assert mock_logger.info.call_count >= 2
    assert mock_logger.debug.call_count >= 2


@patch("pipeline.host_processing_pipeline.logger")
def test_transform_method(mock_logger, mock_config):
    """Test the _transform method that normalizes and deduplicates data."""
    pipeline = HostProcessingPipeline(mock_config)

    # Sample input data
    hosts = [
        {"hostname": "host1", "ip": "192.168.1.1", "source": "source1"},
        {"hostname": "host2", "ip": "192.168.1.2", "source": "source2"},
    ]

    # Call _transform method
    result = pipeline._transform(hosts)

    # Check that normalizer and deduplicator were called
    mock_config.normalizer.process.assert_called_once_with(hosts)
    mock_config.deduplicator.process.assert_called_once_with(
        mock_config.normalizer.process.return_value
    )

    # Check that we got the expected result
    assert len(result) == 2
    assert result[0]["hostname"] == "host1"
    assert result[1]["hostname"] == "host2"

    # Check that logging happened
    assert mock_logger.info.call_count >= 2


@patch("pipeline.host_processing_pipeline.logger")
def test_load_method(mock_logger, mock_config):
    """Test the _load method that stores data to storage."""
    pipeline = HostProcessingPipeline(mock_config)

    # Sample data to store
    hosts = [
        {"hostname": "host1", "ip": "192.168.1.1", "source": "source1"},
        {"hostname": "host2", "ip": "192.168.1.2", "source": "source2"},
    ]

    # Call _load method
    pipeline._load(hosts)

    # Check that storage was called
    mock_config.storage.save.assert_called_once_with(hosts)

    # Check that logging happened
    assert mock_logger.info.call_count >= 1


@patch("pipeline.host_processing_pipeline.logger")
def test_visualize_method(mock_logger, mock_config):
    """Test the _visualize method that generates visualizations."""
    pipeline = HostProcessingPipeline(mock_config)

    # Sample data for visualization
    hosts = [
        {"hostname": "host1", "ip": "192.168.1.1", "source": "source1"},
        {"hostname": "host2", "ip": "192.168.1.2", "source": "source2"},
    ]

    # Call _visualize method
    pipeline._visualize(hosts)

    # Check that visualizer was called
    mock_config.visualizer.generate.assert_called_once()

    # Check that logging happened
    assert mock_logger.info.call_count >= 2


@patch("pipeline.host_processing_pipeline.logger")
def test_run_method(mock_logger, mock_config):
    """Test the complete run method that executes the pipeline."""
    pipeline = HostProcessingPipeline(mock_config)

    # Mock pipeline methods to check if they are called
    pipeline._extract = MagicMock(
        return_value=[{"hostname": "host1"}, {"hostname": "host2"}]
    )
    pipeline._transform = MagicMock(
        return_value=[{"hostname": "host1", "normalized": True}]
    )
    pipeline._load = MagicMock()
    pipeline._visualize = MagicMock()

    # Call run method
    pipeline.run()

    # Check that all methods were called in order
    pipeline._extract.assert_called_once()
    pipeline._transform.assert_called_once_with(pipeline._extract.return_value)
    pipeline._load.assert_called_once_with(pipeline._transform.return_value)
    pipeline._visualize.assert_called_once_with(pipeline._transform.return_value)

    # Check that logging happened
    assert mock_logger.info.call_count >= 8  # Multiple log messages in run method
