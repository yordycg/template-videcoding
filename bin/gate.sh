#!/usr/bin/env bash
# gate.sh — Gate pre-commit del flujo videcoding.
# Verifica: lint + tests + integridad de tasks.yaml.
set -euo pipefail

echo "→ [gate] Lint..."
just lint

echo "→ [gate] Tests..."
just test

echo "→ [gate] Verificando tareas e integridad del grafo (tasks.yaml)..."
python3 bin/task.py check

echo "✓ [gate] OK: listo para commit."
