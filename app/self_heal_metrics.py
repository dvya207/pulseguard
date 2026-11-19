import json
from pathlib import Path

from prometheus_client import REGISTRY
from prometheus_client.core import CounterMetricFamily

METRICS_FILE = (
    Path(__file__).resolve().parent.parent
    / "self_heal"
    / "metrics.json"
)

METRIC_NAMES = {
    "self_heal_failures_detected_total": "Detected application failures",
    "self_heal_recovery_attempts_total": "Recovery attempts",
    "self_heal_success_total": "Successful recoveries",
    "self_heal_failure_total": "Failed recoveries",
    "self_heal_rollback_total": "Deployment rollbacks",
}


class SelfHealMetricsCollector:
    def collect(self):
        try:
            with METRICS_FILE.open("r", encoding="utf-8") as file:
                values = json.load(file)
        except (OSError, json.JSONDecodeError):
            values = {}

        for name, description in METRIC_NAMES.items():
            metric = CounterMetricFamily(
                name.removesuffix("_total"),
                description,
            )
            metric.add_metric([], float(values.get(name, 0)))
            yield metric


def register_self_heal_metrics():
    REGISTRY.register(SelfHealMetricsCollector())
