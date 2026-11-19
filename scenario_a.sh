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
    echo "[Scenario A] A deployed version is required. Current status: $STATUS"
    exit 1
fi

echo "[Scenario A] Current version: $ORIGINAL_CURRENT"
echo "[Scenario A] Previous version: $ORIGINAL_PREVIOUS"

./chaos.sh health
./self_heal.sh

FINAL_STATUS=$(python3 -c 'import json; print(json.load(open("state.json"))["status"])')
FINAL_VERSION=$(python3 -c 'import json; print(json.load(open("state.json"))["current_version"])')

if [[ "$FINAL_STATUS" == "deployed" && "$FINAL_VERSION" == "$ORIGINAL_CURRENT" ]]; then
    echo "[Scenario A] PASS: Current version recovered successfully."
elif [[ "$FINAL_STATUS" == "rolled_back" && "$FINAL_VERSION" == "$ORIGINAL_PREVIOUS" ]]; then
    echo "[Scenario A] PASS: Rollback restored the previous version."
else
    echo "[Scenario A] FAIL: Version or deployment status mismatch."
    echo "Expected current: $ORIGINAL_CURRENT"
    echo "Expected rollback: $ORIGINAL_PREVIOUS"
    echo "Actual version: $FINAL_VERSION"
    echo "Actual status: $FINAL_STATUS"
    exit 1
fi
