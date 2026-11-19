#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")"

if [[ $# -ne 1 ]]; then
    echo "Usage: ./deploy.sh <version-tag>"
    exit 1
fi

TAG="$1"

if [[ ! "$TAG" =~ ^[a-zA-Z0-9_][a-zA-Z0-9_.-]*$ ]]; then
    echo "Invalid image tag."
    exit 1
fi

STATE_FILE="state.json"
IMAGE="pulseguard:$TAG"
HEALTH_URL="http://127.0.0.1:8000/health"

command -v docker >/dev/null || { echo "Docker is required."; exit 1; }
command -v curl >/dev/null || { echo "curl is required."; exit 1; }
command -v python3 >/dev/null || { echo "Python is required."; exit 1; }

if [[ ! -f "$STATE_FILE" ]]; then
    echo "state.json is missing."
    exit 1
fi

CURRENT=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('current_version', ''))")

if [[ -z "$CURRENT" ]]; then
    echo "No current version recorded. Cannot safely deploy."
    exit 1
fi

if [[ "$TAG" == "$CURRENT" ]]; then
    echo "This version is already recorded as current."
    exit 1
fi

echo "[deploy] Building $IMAGE"

if ! docker build -t "$IMAGE" .; then
    echo "[deploy] Image build failed. Existing application remains untouched."
    exit 1
fi

python3 - "$STATE_FILE" "$CURRENT" "$TAG" <<'PY'
import json, sys
from datetime import datetime, timezone
path, current, target = sys.argv[1:]
with open(path) as f:
    state = json.load(f)
state.update({
    "current_version": target,
    "previous_version": current,
    "status": "deploying",
    "timestamp": datetime.now(timezone.utc).isoformat()
})
with open(path + ".tmp", "w") as f:
    json.dump(state, f, indent=2)
    f.write("\n")
import os
os.replace(path + ".tmp", path)
PY

echo "[deploy] Starting $IMAGE"

if ! PULSEGUARD_IMAGE="$IMAGE" PULSEGUARD_VERSION="$TAG" docker compose up -d --no-build pulseguard; then
    echo "[deploy] Startup failed. Rolling back."
    ./rollback.sh "$TAG" || echo "[deploy] Automatic rollback failed."
    exit 1
fi

for i in $(seq 1 12); do
    if [[ "${SIMULATE_FAILURE:-false}" != "true" ]] &&
       curl -fsS "$HEALTH_URL" >/dev/null; then

        python3 - "$STATE_FILE" "$TAG" <<'PY'
import json, sys
from datetime import datetime, timezone
path, version = sys.argv[1:]
with open(path) as f:
    state = json.load(f)
state.update({
    "current_version": version,
    "status": "deployed",
    "timestamp": datetime.now(timezone.utc).isoformat()
})
with open(path + ".tmp", "w") as f:
    json.dump(state, f, indent=2)
    f.write("\n")
import os
os.replace(path + ".tmp", path)
PY
        echo "[deploy] Deployment successful: $TAG"
        exit 0
    fi

    echo "[deploy] Health check failed or failure simulation enabled ($i/12)."
    sleep 5
done

echo "[deploy] Deployment unsuccessful. Starting automatic rollback."

if ./rollback.sh "$TAG"; then
    echo "[deploy] Previous version restored successfully."
else
    echo "[deploy] CRITICAL: Automatic rollback failed. Check the application."
fi

exit 1
