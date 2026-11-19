#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")"

read -r ORIGINAL_CURRENT ORIGINAL_PREVIOUS STATUS < <(
    python3 -c '
import json
s = json.load(open("state.json"))
print(s["current_version"], s["previous_version"], s["status"])
'
)

if [[ "$STATUS" != "deployed" ]]; then
    echo "[Scenario C] A deployed version is required. Current status: $STATUS"
    exit 1
fi

echo "=================================="
echo "       SCENARIO C: FULL TEST"
echo "=================================="
echo "Starting current version: $ORIGINAL_CURRENT"
echo "Starting previous version: $ORIGINAL_PREVIOUS"

echo
echo "[Scenario C] Running Scenario A..."
./scenario_a.sh

CURRENT_STATUS=$(python3 -c 'import json; print(json.load(open("state.json"))["status"])')

if [[ "$CURRENT_STATUS" != "deployed" ]]; then
    echo "[Scenario C] Scenario A resulted in rollback."
    echo "[Scenario C] Scenario B cannot safely run against the original deployment."
    exit 1
fi

echo
echo "[Scenario C] Running Scenario B..."
./scenario_b.sh

echo
echo "=================================="
echo "          FINAL SUMMARY"
echo "=================================="

python3 - <<'PY'
import json

with open("state.json", encoding="utf-8") as f:
    state = json.load(f)

with open("self_heal/metrics.json", encoding="utf-8") as f:
    metrics = json.load(f)

print("Current version :", state.get("current_version"))
print("Previous version:", state.get("previous_version"))
print("Deployment status:", state.get("status"))
print("\nSelf-healing metrics:")
for key, value in metrics.items():
    print(f"  {key}: {value}")
PY

echo
echo "[Scenario C] Both scenarios completed."
