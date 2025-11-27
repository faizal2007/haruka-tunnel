#!/bin/bash
# Haruka Tunnel Startup Script
# Automatically activates venv and runs pytunnel.py

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Source .env to get PYTHON_BIN if available
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Use PYTHON_BIN from .env or default to venv/bin/python
PYTHON_BIN="${PYTHON_BIN:-venv/bin/python}"

# Check if python binary exists
if [ ! -f "$PYTHON_BIN" ]; then
    echo "❌ Python binary not found at: $PYTHON_BIN"
    echo "   Please check your PYTHON_BIN setting in .env or ensure venv is set up"
    exit 1
fi

echo "🚀 Starting Haruka Tunnel"
echo "   Python: $PYTHON_BIN"
echo "   Working Directory: $SCRIPT_DIR"
echo ""

# Run pytunnel.py with the correct Python interpreter
exec "$PYTHON_BIN" "$SCRIPT_DIR/pytunnel.py" "$@"
