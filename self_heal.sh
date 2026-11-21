#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")"

METRICS="self_heal/metrics.json"
STATE="state.json"
HEALTH_URL="http://127.0.0.1:8000/health"

update_metric() {
    python3 - "$METRICS" "$1" <<'PY'
import json, os, sys

path, key = sys.argv[1:]
with open(path, encoding="utf-8") as f:
    data = json.load(f)

data[key] = data.get(key, 0) + 1
tmp = path + ".tmp"

with open(tmp, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    f.write("\n")

os.replace(tmp, path)
PY
}

check_health() {
    curl -fsS "$HEALTH_URL" >/dev/null 2>&1
}

if check_health; then
    echo "[watchdog] PulseGuard is healthy."
    exit 0
fi

echo "[watchdog] Health check failed."
update_metric self_heal_failures_detected_total

STATUS=$(python3 -c 'import json; print(json.load(open("state.json"))["status"])')

if [[ "$STATUS" != "deployed" ]]; then
    echo "[watchdog] Recovery skipped. Deployment status: $STATUS"
    exit 1
fi

CURRENT=$(python3 -c 'import json; print(json.load(open("state.json"))["current_version"])')

update_metric self_heal_recovery_attempts_total

echo "[watchdog] Attempting to restart current version: $CURRENT"

if PULSEGUARD_IMAGE="pulseguard:$CURRENT" \
   PULSEGUARD_VERSION="$CURRENT" \
   docker compose up -d --no-build --force-recreate pulseguard; then

    for attempt in {1..12}; do
        if check_health; then
            update_metric self_heal_success_total
            echo "[watchdog] Current version recovered successfully."
            exit 0
        fi
        sleep 5
    done
fi

echo "[watchdog] Current version recovery failed. Attempting rollback..."

if ./rollback.sh; then
    update_metric self_heal_success_total
    update_metric self_heal_rollback_total
    echo "[watchdog] Rollback recovery successful."
    exit 0
fi

update_metric self_heal_failure_total
echo "[watchdog] Recovery and rollback both failed."
exit 1
