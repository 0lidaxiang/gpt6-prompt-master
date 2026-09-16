#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 1 ]]; then
  echo '用法: bash rollback.sh <快照目录>' >&2
  exit 2
fi
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/file_guard.py" rollback "$1"
