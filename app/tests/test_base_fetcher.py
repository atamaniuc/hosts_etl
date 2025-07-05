from unittest.mock import patch, Mock
from fetchers.base import BaseFetcher


class MockFetcher(BaseFetcher):
    """Mock fetcher for testing BaseFetcher functionality"""


def test_pagination_with_page_size_2():
    """Test pagination with page_size=2"""
    fetcher = MockFetcher("http://test.com", "test")

    with patch("fetchers.base.requests.post") as mock_post:
        # Mock first page with 2 items
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = [
            {"hostname": "host1", "ip": "1.1.1.1"},
            {"hostname": "host2", "ip": "1.1.1.2"},
        ]
        mock_response1.raise_for_status.return_value = None

        # Mock second page with 1 item (less than page_size)
        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = [{"hostname": "host3", "ip": "1.1.1.3"}]
        mock_response2.raise_for_status.return_value = None

        mock_post.side_effect = [mock_response1, mock_response2]

        with patch("fetchers.base.os.getenv") as mock_getenv:
            mock_getenv.return_value = "test_token"

            result = fetcher.fetch()

            # Should have 3 hosts total
            assert len(result) == 3
            assert result[0]["hostname"] == "host1"
            assert result[1]["hostname"] == "host2"
            assert result[2]["hostname"] == "host3"


def test_pagination_stops_on_500():
    """Test that pagination stops when server returns 500"""
    fetcher = MockFetcher("http://test.com", "test")

    with patch("fetchers.base.requests.post") as mock_post:
        # Mock first page with 2 items
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = [
            {"hostname": "host1", "ip": "1.1.1.1"},
            {"hostname": "host2", "ip": "1.1.1.2"},
        ]
        mock_response1.raise_for_status.return_value = None

        # Mock second page with 500 error
        mock_response2 = Mock()
        mock_response2.status_code = 500
        mock_response2.text = "invalid skip/limit combo"  # Add text attribute
        mock_response2.raise_for_status.side_effect = Exception("500 error")

        # Mock third page with 1 item (hybrid pagination)
        mock_response3 = Mock()
        mock_response3.status_code = 200
        mock_response3.json.return_value = [{"hostname": "host3", "ip": "1.1.1.3"}]

        mock_post.side_effect = [mock_response1, mock_response2, mock_response3]

        with patch("fetchers.base.os.getenv") as mock_getenv:
            mock_getenv.return_value = "test_token"

            result = fetcher.fetch()

            # Should get 3 hosts total (2 from first page + 1 from hybrid pagination)
            assert len(result) == 3
            assert result[0]["hostname"] == "host1"
            assert result[1]["hostname"] == "host2"
            assert result[2]["hostname"] == "host3"
