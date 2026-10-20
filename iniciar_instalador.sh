#!/usr/bin/env bash
# ==============================================================================
# Lanzador del Instalador de Juegos & Repacks para Linux (Anti-ISDone / unarc)
# ==============================================================================
set -euo pipefail

SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
PROJECT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"

export PATH="$PROJECT_DIR/runtime:$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

cd "$PROJECT_DIR"

if [[ -x "$PROJECT_DIR/venv/bin/python3" ]]; then
    exec "$PROJECT_DIR/venv/bin/python3" "$PROJECT_DIR/main.py" "$@"
else
    exec python3 "$PROJECT_DIR/main.py" "$@"
fi
