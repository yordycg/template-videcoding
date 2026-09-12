#!/usr/bin/env bash
# gate.sh — Gate pre-commit del flujo videcoding.
# Verifica: lint + tests + dual-write (TASKS.md <-> Project.canvas).
set -euo pipefail

echo "→ [gate] Lint..."
just lint

echo "→ [gate] Tests..."
just test

echo "→ [gate] Verificando dual-write (TASKS.md ↔ Project.canvas)..."
python3 bin/sync-tracking.py --check

echo "✓ [gate] OK: listo para commit."
