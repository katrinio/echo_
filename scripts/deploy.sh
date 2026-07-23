#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/home/katrin/projects/echo_"

timestamp() {
  date '+%Y-%m-%d %H:%M:%S'
}

log() {
  local level="$1"
  shift
  printf '%s %-5s %s\n' "$(timestamp)" "$level" "$*"
}

main() {
  log INFO "Starting deployment"

  if [[ ! -d "$REPO_DIR" ]]; then
    log ERROR "Repository directory not found: $REPO_DIR"
    exit 1
  fi

  cd "$REPO_DIR"
  log INFO "Using repository: $REPO_DIR"

  local previous_commit
  previous_commit="$(git rev-parse --short HEAD)"

  log INFO "Fetching latest code from origin/main"
  git fetch origin main

  local target_commit
  target_commit="$(git rev-parse --short origin/main)"

  if [[ "$previous_commit" == "$target_commit" ]]; then
    log INFO "Repository already up to date at commit $target_commit"
  else
    git reset --hard origin/main >/dev/null
    log INFO "Repository updated: $previous_commit -> $target_commit"
  fi

  log INFO "Building and starting containers"
  local start_time
  start_time="$(date +%s)"
  docker compose up -d --build
  local end_time
  end_time="$(date +%s)"
  local duration
  duration=$((end_time - start_time))
  log INFO "Containers started in ${duration}s"

  local services_up
  services_up="$(docker compose ps --services --status running | wc -l | tr -d ' ')"
  if [[ "$services_up" -eq 0 ]]; then
    log WARN "No running services reported by docker compose"
  else
    log INFO "Running services: $services_up"
  fi

  log INFO "Deployment completed successfully"
}

main "$@"
