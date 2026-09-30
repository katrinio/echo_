#!/usr/bin/env bash
set -euo pipefail

cd /home/katrin/projects/echo_

git fetch origin main
git reset --hard origin/main

echo_version="$(git rev-parse --short HEAD)"
echo "Deploying Echo version: ${echo_version}"

if ! command -v infisical >/dev/null 2>&1; then
  echo "Infisical CLI is not installed"
  exit 1
fi

infisical_auth_file="${INFISICAL_AUTH_FILE:-$HOME/.config/infisical/echo-auth.env}"
if [[ ! -r "$infisical_auth_file" ]]; then
  echo "Infisical Machine Identity credentials are missing or unreadable"
  exit 1
fi

# shellcheck disable=SC1090
source "$infisical_auth_file"
: "${INFISICAL_CLIENT_ID:?INFISICAL_CLIENT_ID is missing}"
: "${INFISICAL_CLIENT_SECRET:?INFISICAL_CLIENT_SECRET is missing}"
: "${INFISICAL_PROJECT_ID:?INFISICAL_PROJECT_ID is missing}"

INFISICAL_TOKEN="$(infisical login \
  --method=universal-auth \
  --client-id="$INFISICAL_CLIENT_ID" \
  --client-secret="$INFISICAL_CLIENT_SECRET" \
  --silent \
  --plain)"
export INFISICAL_TOKEN
unset INFISICAL_CLIENT_ID INFISICAL_CLIENT_SECRET

infisical_compose() {
  ECHO_VERSION="$echo_version" infisical run \
    --projectId="$INFISICAL_PROJECT_ID" \
    --env=prod \
    --path=/echo \
    -- docker compose "$@"
}

infisical_compose config --quiet
infisical_compose up -d --build
infisical_compose ps
