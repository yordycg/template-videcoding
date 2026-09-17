#!/usr/bin/env bash
# gate.sh — Gate pre-commit del flujo videcoding.
# Verifica: lint + tests + dual-write (TASKS.md <-> Project.canvas).
set -euo pipefail

echo "→ [gate] Lint..."
just lint

echo "→ [gate] Tests..."
just test

echo "→ [gate] Verificando tareas e integridad del grafo (tasks.yaml)..."
python3 bin/task.py check

echo "✓ [gate] OK: listo para commit."
