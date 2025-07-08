from unittest.mock import patch, MagicMock
import pytest


@patch("main.HostProcessingPipeline")
@patch("main.PipelineConfig")
@patch("main.ChartsVisualizer")
@patch("main.MongoStorage")
@patch("main.DeduplicationProcessor")
@patch("main.HostNormalizer")
@patch("main.CrowdstrikeFetcher")
@patch("main.QualysFetcher")
@patch("main.logger")
@patch("main.time")
def test_main_success(
    mock_time,
    mock_logger,
    mock_qualys,
    mock_crowdstrike,
    mock_normalizer,
    mock_deduplicator,
    mock_storage,
    mock_visualizer,
    mock_config,
    mock_pipeline,
):
    """Test successful execution of the main function."""
    # Setup mocks
    mock_time.time.side_effect = [1000, 1060]  # Start and end times
    mock_qualys_instance = MagicMock()
    mock_crowdstrike_instance = MagicMock()
    mock_qualys.return_value = mock_qualys_instance
    mock_crowdstrike.return_value = mock_crowdstrike_instance

    mock_normalizer_instance = MagicMock()
    mock_normalizer.return_value = mock_normalizer_instance

    mock_deduplicator_instance = MagicMock()
    mock_deduplicator.return_value = mock_deduplicator_instance

    mock_storage_instance = MagicMock()
    mock_storage.return_value = mock_storage_instance

    mock_visualizer_instance = MagicMock()
    mock_visualizer.return_value = mock_visualizer_instance

    mock_config_instance = MagicMock()
    mock_config.return_value = mock_config_instance

    mock_pipeline_instance = MagicMock()
    mock_pipeline.return_value = mock_pipeline_instance

    # Import and run main
    from main import main

    main()

    # Verify components creation
    mock_qualys.assert_called_once()
    mock_crowdstrike.assert_called_once()
    mock_normalizer.assert_called_once()
    mock_deduplicator.assert_called_once()
    mock_storage.assert_called_once()
    mock_visualizer.assert_called_once()

    # Verify pipeline creation and execution
    mock_config.assert_called_once_with(
        fetchers=[mock_qualys_instance, mock_crowdstrike_instance],
        normalizer=mock_normalizer_instance,
        deduplicator=mock_deduplicator_instance,
        storage=mock_storage_instance,
        visualizer=mock_visualizer_instance,
    )
    mock_pipeline.assert_called_once_with(mock_config_instance)
    mock_pipeline_instance.run.assert_called_once()

    # Verify logging
    assert mock_logger.info.call_count >= 4

    # Verify time tracking
    assert mock_time.time.call_count == 2


@patch("main.HostProcessingPipeline")
@patch("main.PipelineConfig")
@patch("main.ChartsVisualizer")
@patch("main.MongoStorage")
@patch("main.DeduplicationProcessor")
@patch("main.HostNormalizer")
@patch("main.CrowdstrikeFetcher")
@patch("main.QualysFetcher")
@patch("main.logger")
@patch("main.time")
def test_main_exception(
    mock_time,
    mock_logger,
    mock_qualys,
    mock_crowdstrike,
    mock_normalizer,
    mock_deduplicator,
    mock_storage,
    mock_visualizer,
    mock_config,
    mock_pipeline,
):
    """Test error handling in the main function."""
    # Setup mocks
    mock_time.time.side_effect = [1000, 1030]  # Start and end times
    mock_pipeline_instance = MagicMock()
    mock_pipeline.return_value = mock_pipeline_instance
    mock_pipeline_instance.run.side_effect = Exception("Test error")

    # Import and run main, expecting exception
    from main import main

    with pytest.raises(Exception) as exc_info:
        main()

    assert str(exc_info.value) == "Test error"

    # Verify logging of error
    mock_logger.error.assert_called()

    # Verify time tracking for failed execution
    assert mock_time.time.call_count == 2


def test_dotenv_loading():
    """Test that environment variables are loaded."""
    # Patch load_dotenv using pytest.monkeypatch
    import sys

    # Remove main from sys.modules if already imported
    if "main" in sys.modules:
        del sys.modules["main"]

    # Patch load_dotenv directly in dotenv module before importing main
    with patch("dotenv.load_dotenv") as mock_load_dotenv:
        # Import main again
        import main

        # Check that load_dotenv was called
        mock_load_dotenv.assert_called_once()


@patch("main.logging.FileHandler")
@patch("main.logging.StreamHandler")
def test_logging_setup(mock_stream_handler, mock_file_handler):
    """Test logging configuration."""
    # Reset logging to remove effects from previous imports
    import logging

    logging.root.handlers = []

    # Re-import module to trigger logging setup
    import importlib
    import main

    importlib.reload(main)

    # Verify logging handlers
    mock_file_handler.assert_called_once_with("etl_pipeline.log")
    mock_stream_handler.assert_called_once()
