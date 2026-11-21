#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")"

STATE_FILE="state.json"
HEALTH_URL="http://127.0.0.1:8000/health"

if [[ ! -f "$STATE_FILE" ]]; then
    echo "[rollback] State file missing."
    exit 1
fi

PREVIOUS=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('previous_version', ''))")

if [[ -z "$PREVIOUS" ]]; then
    echo "[rollback] No previous version available."
    exit 1
fi

IMAGE="pulseguard:$PREVIOUS"

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    echo "[rollback] Previous image $IMAGE does not exist."
    exit 1
fi

CURRENT=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('current_version', ''))")

echo "[rollback] Restoring $IMAGE"

if ! PULSEGUARD_IMAGE="$IMAGE" PULSEGUARD_VERSION="$PREVIOUS" docker compose up -d --no-build pulseguard; then
    echo "[rollback] Container startup failed."
    exit 1
fi

for i in $(seq 1 12); do
    if curl -fsS "$HEALTH_URL" >/dev/null; then
        python3 - "$STATE_FILE" "$PREVIOUS" "$CURRENT" <<'PY'
import json, sys
from datetime import datetime, timezone
path, restored, failed = sys.argv[1:]
with open(path) as f:
    state = json.load(f)
state.update({
    "current_version": restored,
    "previous_version": failed,
    "status": "rolled_back",
    "timestamp": datetime.now(timezone.utc).isoformat()
})
with open(path + ".tmp", "w") as f:
    json.dump(state, f, indent=2)
    f.write("\n")
import os
os.replace(path + ".tmp", path)
PY
        echo "[rollback] Success. Running version: $PREVIOUS"
        exit 0
    fi

    echo "[rollback] Waiting for health check ($i/12)..."
    sleep 5
done

echo "[rollback] Health check failed."
exit 1
