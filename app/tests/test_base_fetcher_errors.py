from unittest.mock import patch, Mock

import pytest
import requests
from fetchers.base import BaseFetcher


# Create a concrete implementation of the abstract BaseFetcher class for testing
# Using pytest.markonly to avoid collecting this class as a test
class TestFetcher(BaseFetcher):
    """Test implementation of BaseFetcher"""

    __test__ = False  # This tells pytest not to collect this class as a test

    def __init__(self):
        super().__init__("https://test-api.example.com", "test_source")

    def fetch(self):
        return super().fetch()


@patch("fetchers.base.requests.post")
@patch("fetchers.base.logger")
def test_handle_api_error_pagination_end(mock_logger, mock_post):
    """Test handling of API errors related to pagination limits"""
    fetcher = TestFetcher()

    # Create mock response to simulate pagination end error
    mock_response_error = Mock()
    mock_response_error.status_code = 400
    mock_response_error.text = "Invalid skip/limit combo"
    mock_response_error.json.side_effect = ValueError("Invalid JSON")

    # Create mock response for the last request with page_size=1
    mock_response_success = Mock()
    mock_response_success.status_code = 200
    # Note that we return a list of objects directly, not an object with a data field
    mock_response_success.json.return_value = [{"hostname": "last-host"}]

    # Configure the sequence of calls to requests.post
    mock_post.side_effect = [mock_response_success]

    # Call the _handle_api_error method
    should_break, hosts = fetcher._handle_api_error(mock_response_error, 10)

    # Check that the method returned the correct values
    assert should_break is True
    assert len(hosts) == 1
    assert hosts[0]["hostname"] == "last-host"
    assert hosts[0]["source"] == "test_source"
    assert mock_post.call_count == 1


@patch("fetchers.base.requests.post")
@patch("fetchers.base.logger")
def test_handle_api_error_with_rate_limit(mock_logger, mock_post):
    """Test handling of API rate limiting errors"""
    fetcher = TestFetcher()

    # Create mock response to simulate rate limit error
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.text = "Rate limit exceeded"

    # Simulate that rate limit handling raises raise_for_status()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "429 Rate limit exceeded"
    )

    # Call the _handle_api_error method
    try:
        should_break, hosts = fetcher._handle_api_error(mock_response, 0)
        assert False, "Should have raised an exception"
    except requests.exceptions.HTTPError:
        # This is the expected behavior
        pass

    # Check that the appropriate log was called
    mock_logger.error.assert_called()


@patch("fetchers.base.requests.post")
@patch("fetchers.base.logger")
def test_handle_api_error_with_server_error(mock_logger, mock_post):
    """Test handling of server errors (5xx)"""
    fetcher = TestFetcher()

    # Create mock response to simulate server error
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    # In this test, we need to verify that the error text doesn't contain pagination end indicators
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "500 Server Error"
    )

    # Call the _handle_api_error method
    try:
        should_break, hosts = fetcher._handle_api_error(mock_response, 0)
        assert False, "Should have raised an exception"
    except requests.exceptions.HTTPError:
        # This is the expected behavior
        pass

    # Check that the appropriate log was called
    mock_logger.error.assert_called()


@patch("fetchers.base.requests.post")
@patch("fetchers.base.logger")
def test_fetch_with_auth_error(mock_logger, mock_post):
    """Test fetch with authentication error"""
    fetcher = TestFetcher()

    # Create mock response to simulate authentication error
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "401 Unauthorized"
    )
    mock_post.return_value = mock_response

    # Call the fetch method and expect an exception
    with pytest.raises(requests.exceptions.HTTPError):
        fetcher.fetch()

    # Check that the appropriate log was called
    mock_logger.error.assert_called()


@patch("fetchers.base.requests.post")
@patch("fetchers.base.logger")
def test_fetch_with_connection_error(mock_logger, mock_post):
    """Test fetch with connection error"""
    fetcher = TestFetcher()

    # Simulate a connection error
    mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

    # Call the fetch method and expect an exception
    with pytest.raises(requests.exceptions.ConnectionError):
        fetcher.fetch()

    # Check that the appropriate log was called
    mock_logger.error.assert_called()
