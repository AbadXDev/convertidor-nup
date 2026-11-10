#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON=${PYTHON:-python3}
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo 'Se requiere Python 3.10 o posterior. Consulta linux/README.md.' >&2
    exit 1
fi
if ! "$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo 'Se requiere Python 3.10 o posterior.' >&2
    exit 1
fi
exec "$PYTHON" "$SCRIPT_DIR/convertidor_nup.py" "$@"
