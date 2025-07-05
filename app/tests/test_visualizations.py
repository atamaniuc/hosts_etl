from datetime import datetime, timedelta
from unittest.mock import patch
from visualizations.charts import ChartsVisualizer


@patch("visualizations.charts.collection.find")
def test_generate_visualizations(mock_find):
    """Test basic visualization generation"""
    mock_find.return_value = [{"os": "linux", "last_seen": "2023-01-01T00:00:00"}]
    vis = ChartsVisualizer()
    result = vis.generate()
    assert "total_hosts" in result
    assert "by_source" in result
    assert "by_os" in result


def test_normalize_os_name():
    """Test OS name normalization"""
    vis = ChartsVisualizer()

    # Test various OS names
    assert vis.normalize_os_name("Amazon Linux 2") == "Linux"
    assert vis.normalize_os_name("Microsoft Windows Server 2019") == "Windows"
    assert vis.normalize_os_name("Mac OS X") == "macOS"
    assert vis.normalize_os_name("Ubuntu 20.04") == "Ubuntu"
    assert vis.normalize_os_name("CentOS 7") == "CentOS"
    assert (
        vis.normalize_os_name("Red Hat Enterprise Linux") == "Linux"
    )  # "linux" matches first
    assert vis.normalize_os_name("Unknown OS") == "Other"
    assert vis.normalize_os_name("") == "Unknown"
    assert vis.normalize_os_name(None) == "Unknown"


@patch("visualizations.charts.collection.find")
@patch("visualizations.charts.plt.savefig")
@patch("visualizations.charts.plt.close")
@patch("visualizations.charts.os.makedirs")
def test_create_os_distribution_chart(
    mock_makedirs, mock_close, mock_savefig, mock_find
):
    """Test OS distribution chart creation"""
    mock_find.return_value = [
        {"os": "Amazon Linux 2", "source": "qualys"},
        {"os": "Windows Server 2019", "source": "crowdstrike"},
        {"os": "Mac OS X", "source": "qualys"},
    ]

    vis = ChartsVisualizer()
    result = vis.generate()

    # Check that chart creation was called
    mock_savefig.assert_called()
    mock_close.assert_called()
    mock_makedirs.assert_called_with("visualizations/images", exist_ok=True)

    # Check OS normalization results
    assert result["by_os"]["Linux"] == 1
    assert result["by_os"]["Windows"] == 1
    assert result["by_os"]["macOS"] == 1


@patch("visualizations.charts.collection.find")
@patch("visualizations.charts.plt.savefig")
@patch("visualizations.charts.plt.close")
@patch("visualizations.charts.os.makedirs")
def test_create_source_distribution_chart(
    mock_makedirs, mock_close, mock_savefig, mock_find
):
    """Test source distribution chart creation"""
    mock_find.return_value = [
        {"os": "Linux", "source": "qualys"},
        {"os": "Windows", "source": "qualys"},
        {"os": "Mac", "source": "crowdstrike"},
    ]

    vis = ChartsVisualizer()
    result = vis.generate()

    # Check that chart creation was called
    mock_savefig.assert_called()
    mock_close.assert_called()

    # Check source distribution
    assert result["by_source"]["qualys"] == 2
    assert result["by_source"]["crowdstrike"] == 1


@patch("visualizations.charts.collection.find")
@patch("visualizations.charts.plt.savefig")
@patch("visualizations.charts.plt.close")
@patch("visualizations.charts.os.makedirs")
def test_create_host_freshness_chart(
    mock_makedirs, mock_close, mock_savefig, mock_find
):
    """Test host freshness chart creation"""
    # Create test data with old and recent hosts
    old_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%S")
    recent_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%S")

    mock_find.return_value = [
        {"os": "Linux", "last_seen": old_date},
        {"os": "Windows", "last_seen": recent_date},
        {"os": "Mac", "last_seen": None},  # Should be counted as old
    ]

    vis = ChartsVisualizer()
    result = vis.generate()

    # Check that chart creation was called
    mock_savefig.assert_called()
    mock_close.assert_called()

    # Check freshness distribution
    assert result["old_hosts"] == 2  # old_date + None
    assert result["recent_hosts"] == 1  # recent_date


@patch("visualizations.charts.collection.find")
def test_empty_data_handling(mock_find):
    """Test handling of empty data"""
    mock_find.return_value = []

    vis = ChartsVisualizer()
    result = vis.generate()

    assert result["total_hosts"] == 0
    assert not result["by_source"]
    assert not result["by_os"]
    assert result["old_hosts"] == 0
    assert result["recent_hosts"] == 0


@patch("visualizations.charts.collection.find")
def test_invalid_date_handling(mock_find):
    """Test handling of invalid date formats"""
    mock_find.return_value = [
        {"os": "Linux", "last_seen": "invalid-date-format"},
        {"os": "Windows", "last_seen": "2023-01-01T00:00:00"},
    ]

    vis = ChartsVisualizer()
    result = vis.generate()

    # Both dates are old (invalid format + old date from 2023)
    assert result["old_hosts"] == 2
    assert result["recent_hosts"] == 0


@patch("visualizations.charts.collection.find")
@patch("visualizations.charts.plt.savefig")
@patch("visualizations.charts.plt.close")
@patch("visualizations.charts.os.makedirs")
def test_chart_file_creation(mock_makedirs, mock_close, mock_savefig, mock_find):
    """Test that chart files are created with correct parameters"""
    mock_find.return_value = [{"os": "Linux", "source": "qualys"}]

    vis = ChartsVisualizer()
    vis.generate()

    # Check that savefig was called with correct parameters
    mock_savefig.assert_called()
    calls = mock_savefig.call_args_list

    # Should have 3 calls (os_distribution, source_distribution, host_age_pie)
    assert len(calls) == 3

    # Check that each call has correct parameters
    for call in calls:
        args, kwargs = call
        assert kwargs.get("dpi") == 300
        assert kwargs.get("bbox_inches") == "tight"
        assert ".png" in args[0]
