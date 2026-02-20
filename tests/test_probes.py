from network_monitor import probes


def test_result_to_labels_success():
    r = probes.ProbeResult(success=True, latency_ms=10.0, error=None)
    labels = probes.result_to_labels(r)
    assert labels["status"] == "up"
    assert labels["error"] == ""


def test_result_to_labels_failure():
    r = probes.ProbeResult(success=False, latency_ms=None, error="boom")
    labels = probes.result_to_labels(r)
    assert labels["status"] == "down"
    assert labels["error"] == "boom"
