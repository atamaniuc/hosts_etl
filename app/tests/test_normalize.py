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
