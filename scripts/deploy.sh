#!/usr/bin/env bash
set -e

cd /home/katrin/projects/echo_

git fetch origin main
git reset --hard origin/main

docker compose up -d --build
docker compose ps
