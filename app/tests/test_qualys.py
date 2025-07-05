from fetchers.qualys import QualysFetcher
from fetchers.base import BaseFetcher


def test_qualys_fetcher_init():
    """Test that QualysFetcher initializes correctly"""
    fetcher = QualysFetcher()
    assert fetcher.source_name == "qualys"
    assert "qualys" in fetcher.base_url


def test_qualys_fetcher_inheritance():
    """Test that QualysFetcher inherits from BaseFetcher"""
    fetcher = QualysFetcher()
    assert isinstance(fetcher, BaseFetcher)
