#!/usr/bin/env bash

set -euo pipefail

VENV_DIR=".venv"
APP_SCRIPT="src/dashboard.py"

if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_DIR/bin/activate" ]; then
  echo "ERROR: No valid virtual environment found in $VENV_DIR"
  echo "Possible solutions:"
  echo "  • Create the environment:     python3 -m venv $VENV_DIR"
  echo "  • Or with python:             python -m venv $VENV_DIR"
  echo "  • Then install dependencies:  $VENV_DIR/bin/pip install -r requirements.txt"
  exit 1
fi

echo "Activating virtual environment..."

if [ -f "$VENV_DIR/bin/activate" ]; then
  source "$VENV_DIR/bin/activate"
else
  echo "ERROR: Cannot find $VENV_DIR/bin/activate"
  exit 2
fi

if [ -z "${VIRTUAL_ENV:-}" ]; then
  echo "ERROR: Virtual environment could not be activated correctly"
  exit 3
fi

echo "Environment activated → $(python --version 2>&1 | head -n1)"
echo "Launching application..."

python "$APP_SCRIPT" "$@"
