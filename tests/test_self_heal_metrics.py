import json

from app import self_heal_metrics


def test_collector_reads_all_metrics(tmp_path, monkeypatch):
    metrics_file = tmp_path / "metrics.json"
    expected = {
        "self_heal_failures_detected_total": 2,
        "self_heal_recovery_attempts_total": 3,
        "self_heal_success_total": 2,
        "self_heal_failure_total": 1,
        "self_heal_rollback_total": 1,
    }

    metrics_file.write_text(json.dumps(expected), encoding="utf-8")
    monkeypatch.setattr(self_heal_metrics, "METRICS_FILE", metrics_file)

    families = list(self_heal_metrics.SelfHealMetricsCollector().collect())
    actual = {
        sample.name: sample.value
        for family in families
        for sample in family.samples
    }

    assert actual == {key: float(value) for key, value in expected.items()}


def test_collector_returns_zero_for_missing_file(tmp_path, monkeypatch):
    metrics_file = tmp_path / "missing.json"
    monkeypatch.setattr(self_heal_metrics, "METRICS_FILE", metrics_file)

    families = list(self_heal_metrics.SelfHealMetricsCollector().collect())
    actual = {
        sample.name: sample.value
        for family in families
        for sample in family.samples
    }

    assert len(actual) == len(self_heal_metrics.METRIC_NAMES)
    assert all(value == 0 for value in actual.values())


def test_collector_handles_invalid_json(tmp_path, monkeypatch):
    metrics_file = tmp_path / "metrics.json"
    metrics_file.write_text("{invalid json", encoding="utf-8")
    monkeypatch.setattr(self_heal_metrics, "METRICS_FILE", metrics_file)

    families = list(self_heal_metrics.SelfHealMetricsCollector().collect())
    actual = {
        sample.name: sample.value
        for family in families
        for sample in family.samples
    }

    assert len(actual) == len(self_heal_metrics.METRIC_NAMES)
    assert all(value == 0 for value in actual.values())
