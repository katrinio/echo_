#!/usr/bin/env bash
set -e

cd /home/katrin/projects/echo_

git fetch origin main
git reset --hard origin/main

export ECHO_VERSION="$(git rev-parse --short HEAD)"
echo "Deploying Echo version: ${ECHO_VERSION}"

docker compose up -d --build
docker compose ps
