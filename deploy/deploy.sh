#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

BRANCH="${DEPLOY_BRANCH:-main}"

echo "==> Fetching ${BRANCH}"
git fetch origin
git checkout "${BRANCH}"
git reset --hard "origin/${BRANCH}"

echo "==> Building and starting production stack"
docker compose -f docker-compose.prod.yml --env-file .env pull || true
docker compose -f docker-compose.prod.yml --env-file .env up -d --build --remove-orphans

echo "==> Service status"
docker compose -f docker-compose.prod.yml --env-file .env ps

echo "Deploy finished."
