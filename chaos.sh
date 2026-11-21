#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")"

COMMAND="${1:-}"

STATUS=$(python3 -c 'import json; print(json.load(open("state.json"))["status"])')

if [[ "$STATUS" != "deployed" ]]; then
    echo "[chaos] Aborted. Deployment status is: $STATUS"
    echo "[chaos] A deployed version is required."
    exit 1
fi

case "$COMMAND" in
    health)
        echo "[chaos] Triggering simulated health failure..."
        curl -fsS -X POST \
            -H "Content-Type: application/json" \
            -d '{"enabled":true}' \
            http://127.0.0.1:8000/api/v1/simulate-failure
        echo
        ;;

    stop)
        echo "[chaos] Stopping PulseGuard container..."
        docker compose stop pulseguard
        ;;

    both)
        echo "[chaos] Triggering health failure..."
        curl -fsS -X POST \
            -H "Content-Type: application/json" \
            -d '{"enabled":true}' \
            http://127.0.0.1:8000/api/v1/simulate-failure
        echo
        echo "[chaos] Stopping PulseGuard container..."
        docker compose stop pulseguard
        ;;

    *)
        echo "Usage: ./chaos.sh {health|stop|both}"
        exit 1
        ;;
esac
