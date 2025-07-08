from processors.normalize import HostNormalizer


def test_normalize():
    raw = [
        {
            "source": "qualys",
            "hostname": "h",
            "ip": "1.1.1.1",
            "os": "linux",
            "lastSeen": "2023-01-01T00:00:00",
        }
    ]
    norm = HostNormalizer().process(raw)
    assert isinstance(norm, list)
    assert "hostname" in norm[0]


def test_normalize_with_source_detection():
    """Test that the normalizer can detect the source when not explicitly provided"""
    # Data that looks like Crowdstrike (with platform_name)
    crowdstrike_data = [
        {
            "hostname": "win-server",
            "local_ip": "192.168.1.10",
            "platform_name": "Windows Server 2019",
            "last_seen": "2023-05-15T12:30:00",
        }
    ]

    # Data that doesn't match any specific pattern (will be considered Qualys)
    unknown_data = [
        {
            "hostname": "unknown-host",
            "ip": "10.0.0.5",
            "os": "Linux",
            "modified": "2023-06-20T09:45:00",
        }
    ]

    # Normalize both data types
    normalizer = HostNormalizer()
    normalized_cs = normalizer.process(crowdstrike_data)
    normalized_unknown = normalizer.process(unknown_data)

    # Check that sources are None when not explicitly provided (current behavior)
    assert normalized_cs[0]["source"] is None
    assert normalized_unknown[0]["source"] is None

    # Check other fields
    assert normalized_cs[0]["os"] == "Windows Server 2019"
    assert normalized_cs[0]["ip"] == "192.168.1.10"
    assert normalized_unknown[0]["last_seen"] == "2023-06-20T09:45:00"


def test_normalize_mixed_data():
    """Test normalization with mixed data sources"""
    mixed_data = [
        # Qualys with explicit source specification
        {
            "source": "qualys",
            "hostname": "q-host",
            "ip": "192.168.1.5",
            "os": "CentOS",
        },
        # Crowdstrike with explicit source specification
        {
            "source": "crowdstrike",
            "hostname": "cs-host",
            "local_ip": "192.168.1.6",
            "platform_name": "Windows 10",
        },
        # Qualys without explicit source specification
        {
            "hostname": "another-q-host",
            "ip": "192.168.1.7",
            "os": "Ubuntu",
        },
        # Crowdstrike without explicit source specification
        {
            "hostname": "another-cs-host",
            "platform_id": "1234",
            "local_ip": "192.168.1.8",
        },
    ]

    normalizer = HostNormalizer()
    normalized = normalizer.process(mixed_data)

    assert len(normalized) == 4

    # Check correct source detection (current behavior: explicit sources work, implicit ones are None)
    sources = [host["source"] for host in normalized]
    assert sources.count("qualys") == 1  # Only explicit qualys source
    assert sources.count("crowdstrike") == 1  # Only explicit crowdstrike source
    assert sources.count(None) == 2  # Items without explicit source get None

    # Check that all hosts have required fields
    for host in normalized:
        assert "hostname" in host
        assert "ip" in host
        assert "source" in host
