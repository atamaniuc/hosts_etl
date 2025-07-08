from fetchers.base import BaseFetcher
from fetchers.crowdstrike import CrowdstrikeFetcher


def test_crowdstrike_fetcher_init():
    """Test that CrowdstrikeFetcher initializes correctly"""
    fetcher = CrowdstrikeFetcher()
    assert fetcher.source_name == "crowdstrike"
    assert "crowdstrike" in fetcher.base_url


def test_crowdstrike_fetcher_inheritance():
    """Test that CrowdstrikeFetcher inherits from BaseFetcher"""
    fetcher = CrowdstrikeFetcher()
    assert isinstance(fetcher, BaseFetcher)
