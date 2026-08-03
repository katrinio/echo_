#!/usr/bin/env bash
set -e

cd /home/katrin/projects/echo_

git fetch origin main
git reset --hard origin/main

echo_version="$(git rev-parse --short HEAD)"
echo "Deploying Echo version: ${echo_version}"

ECHO_VERSION="${echo_version}" docker compose up -d --build
ECHO_VERSION="${echo_version}" docker compose ps
