#!/usr/bin/env bash
set -euo pipefail
project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
exec docker run --rm --cpus=4 --memory=16g --user "$(id -u):$(id -g)" \
  --env CCACHE_DIR=/workspace/build32/.ccache --env THREADS=4 \
  --mount "type=bind,src=$project_root,dst=/workspace" \
  simt-differential:dev "$@"
