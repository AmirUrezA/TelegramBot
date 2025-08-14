#!/usr/bin/env bash
set -Eeuo pipefail
CONTAINER="postgres_db"
OUT="/var/log/postgresql/postgres_auth_fail.log"
mkdir -p "$(dirname "$OUT")"
touch "$OUT"
chmod 0640 "$OUT"

# Pull last ~minute from Docker logs, keep only auth failures
# Adjust --since to be slightly longer than the timer interval to avoid gaps
if ! command -v docker >/dev/null 2>&1; then
	echo "docker not found" >&2
	exit 1
fi

docker logs "$CONTAINER" --since 70s 2>&1 \
	| grep -E 'FATAL:\s+password authentication failed for user' \
	>> "$OUT" 