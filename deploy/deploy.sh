#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

BRANCH="${DEPLOY_BRANCH:-master}"

echo "==> Fetching ${BRANCH}"
git fetch origin
git checkout "${BRANCH}"
git reset --hard "origin/${BRANCH}"

echo "==> Building and starting production stack"
COMPOSE=(docker compose -f docker-compose.prod.yml --env-file .env)

"${COMPOSE[@]}" pull || true

# Free host :80/:443 before recreate (avoids intermittent bind failures)
"${COMPOSE[@]}" stop caddy || true
"${COMPOSE[@]}" rm -f caddy || true

"${COMPOSE[@]}" up -d --build --remove-orphans

echo "==> Service status"
"${COMPOSE[@]}" ps

echo "Deploy finished."
