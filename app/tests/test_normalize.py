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
    # Данные, похожие на Crowdstrike (с platform_name)
    crowdstrike_data = [
        {
            "hostname": "win-server",
            "local_ip": "192.168.1.10",
            "platform_name": "Windows Server 2019",
            "last_seen": "2023-05-15T12:30:00",
        }
    ]

    # Данные, не похожие ни на что конкретное (будут считаться Qualys)
    unknown_data = [
        {
            "hostname": "unknown-host",
            "ip": "10.0.0.5",
            "os": "Linux",
            "modified": "2023-06-20T09:45:00",
        }
    ]

    # Нормализуем оба типа данных
    normalizer = HostNormalizer()
    normalized_cs = normalizer.process(crowdstrike_data)
    normalized_unknown = normalizer.process(unknown_data)

    # Проверяем, что источники определены правильно
    assert normalized_cs[0]["source"] == "crowdstrike"
    assert normalized_unknown[0]["source"] == "qualys"

    # Проверяем другие поля
    assert normalized_cs[0]["os"] == "Windows Server 2019"
    assert normalized_cs[0]["ip"] == "192.168.1.10"
    assert normalized_unknown[0]["last_seen"] == "2023-06-20T09:45:00"


def test_normalize_mixed_data():
    """Test normalization with mixed data sources"""
    mixed_data = [
        # Qualys с явным указанием источника
        {
            "source": "qualys",
            "hostname": "q-host",
            "ip": "192.168.1.5",
            "os": "CentOS",
        },
        # Crowdstrike с явным указанием источника
        {
            "source": "crowdstrike",
            "hostname": "cs-host",
            "local_ip": "192.168.1.6",
            "platform_name": "Windows 10",
        },
        # Qualys без явного указания источника
        {
            "hostname": "another-q-host",
            "ip": "192.168.1.7",
            "os": "Ubuntu",
        },
        # Crowdstrike без явного указания источника
        {
            "hostname": "another-cs-host",
            "platform_id": "1234",
            "local_ip": "192.168.1.8",
        },
    ]

    normalizer = HostNormalizer()
    normalized = normalizer.process(mixed_data)

    assert len(normalized) == 4

    # Проверяем правильность определения источников
    sources = [host["source"] for host in normalized]
    assert sources.count("qualys") == 2
    assert sources.count("crowdstrike") == 2

    # Проверяем, что все хосты имеют необходимые поля
    for host in normalized:
        assert "hostname" in host
        assert "ip" in host
        assert "source" in host
