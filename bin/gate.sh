#!/usr/bin/env bash
# gate.sh — Gate pre-commit del flujo videcoding.
# Verifica: stack definido + lint + tests + integridad de tasks.yaml.
#
# Salida acotada a propósito: un agente que lee 3.000 líneas de log quema
# contexto y pierde la línea del error. Se imprime 1 línea por paso en verde y
# las últimas MAX_LINES del log cuando algo falla. GATE_VERBOSE=1 muestra todo.
set -euo pipefail

MAX_LINES="${GATE_MAX_LINES:-30}"

run_step() {
    local name="$1"
    shift
    local log rc=0
    log="$(mktemp)"

    if "$@" > "$log" 2>&1; then
        echo "✓ [gate] $name"
    else
        rc=1
        echo "✗ [gate] $name — últimas ${MAX_LINES} líneas:" >&2
        if [ "${GATE_VERBOSE:-0}" = "1" ]; then
            cat "$log" >&2
        else
            tail -n "$MAX_LINES" "$log" >&2
        fi
        echo "  (log completo: GATE_VERBOSE=1 just gate)" >&2
    fi

    rm -f "$log"
    return "$rc"
}

echo "→ [gate] Stack definido (sin stubs de Fase 0)..."
bash bin/check-stubs.sh

echo "→ [gate] Lint..."
run_step "lint" just lint

echo "→ [gate] Tests..."
run_step "test" just test

echo "→ [gate] Tareas e integridad del grafo (tasks.yaml)..."
run_step "tasks.yaml" python3 bin/task.py check

echo "✓ [gate] OK: listo para commit."
