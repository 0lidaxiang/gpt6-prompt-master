#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 3 ]]; then
  echo '用法: bash backup.sh <源文件> <候选稿> <快照输出目录>' >&2
  exit 2
fi
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/file_guard.py" stage "$1" "$2" "$3"
