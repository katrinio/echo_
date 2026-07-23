#!/usr/bin/env bash
set -euo pipefail

timestamp() {
  date '+%Y-%m-%d %H:%M:%S'
}

log_info() {
  printf '%s INFO  %s\n' "$(timestamp)" "$*"
}

log_warn() {
  printf '%s WARN  %s\n' "$(timestamp)" "$*" >&2
}

log_error() {
  printf '%s ERROR %s\n' "$(timestamp)" "$*" >&2
}

extract_build_cache_size() {
  docker system df 2>/dev/null | awk -F '  +' '$1 == "Build Cache" {print $2; exit}'
}

extract_build_cache_reclaimable() {
  docker system df 2>/dev/null | awk -F '  +' '$1 == "Build Cache" {print $3; exit}'
}

extract_reclaimed_space() {
  awk -F ': ' '/Total reclaimed space:/ {print $2; exit}'
}

on_error() {
  local line_no="$1"
  log_error "Cleanup failed at line ${line_no}"
}

trap 'on_error $LINENO' ERR

main() {
  log_info "Starting Docker build cache cleanup"

  if ! command -v docker >/dev/null 2>&1; then
    log_error "Docker CLI not found"
    exit 1
  fi

  local before_size
  before_size="$(extract_build_cache_size || true)"
  if [[ -n "${before_size}" ]]; then
    log_info "Build cache before cleanup: ${before_size}"
  else
    log_warn "Build cache size before cleanup is unavailable"
  fi

  local before_reclaimable
  before_reclaimable="$(extract_build_cache_reclaimable || true)"
  if [[ -n "${before_reclaimable}" ]]; then
    log_info "Build cache reclaimable before cleanup: ${before_reclaimable}"
  fi

  local start_time
  start_time="$(date +%s)"

  local prune_output
  prune_output="$(docker builder prune --all --force 2>&1)"

  local end_time
  end_time="$(date +%s)"
  local duration
  duration=$((end_time - start_time))

  local reclaimed
  reclaimed="$(printf '%s\n' "$prune_output" | extract_reclaimed_space || true)"
  if [[ -n "${reclaimed}" ]]; then
    log_info "Reclaimed: ${reclaimed}"
  else
    log_warn "Reclaimed size was not reported by Docker"
  fi

  local after_size
  after_size="$(extract_build_cache_size || true)"
  if [[ -n "${after_size}" ]]; then
    log_info "Build cache after cleanup: ${after_size}"
  else
    log_warn "Build cache size after cleanup is unavailable"
  fi

  log_info "Cleanup completed successfully in ${duration}s"
}

main "$@"
