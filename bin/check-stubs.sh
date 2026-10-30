#!/usr/bin/env bash
# check-stubs.sh — Bloquea el flujo si lint/test siguen siendo los stubs de la Fase 0.
#
# El template nace con `lint`, `test` y `dev` como placeholders que imprimen un
# aviso y salen con 0. Eso produce un gate "verde" sin haber ejecutado nada.
# Este chequeo detecta el marcador de la Fase 0 en el Justfile y sale con 1.
#
# Uso: bash bin/check-stubs.sh [ruta-al-Justfile]
set -euo pipefail

JUSTFILE="${1:-Justfile}"

if [ ! -f "$JUSTFILE" ]; then
    echo "✗ No se encontró $JUSTFILE (ejecuta desde la raíz del proyecto)." >&2
    exit 1
fi

# Imprime el cuerpo (líneas indentadas) de una receta del Justfile.
recipe_body() {
    awk -v target="$1" '
        $0 ~ "^" target ":[[:space:]]*$" { inside = 1; next }
        inside && /^[A-Za-z0-9_.-]+:/ { exit }
        inside { print }
    ' "$JUSTFILE"
}

missing=()
for target in lint test; do
    if ! grep -qE "^${target}:" "$JUSTFILE"; then
        missing+=("${target}: no existe en el Justfile")
        continue
    fi
    if recipe_body "$target" | grep -q "FASE 0: define"; then
        missing+=("${target}: sigue siendo el stub de la Fase 0")
    fi
done

if [ ${#missing[@]} -gt 0 ]; then
    echo "✗ Gate bloqueado: el stack no está definido todavía." >&2
    printf '  - %s\n' "${missing[@]}" >&2
    echo "  Define las recetas reales (ruff/eslint/pytest/vitest/…) y borra el aviso de Fase 0." >&2
    echo "  Ver AGENTS.md §2 (Fase 0)." >&2
    exit 1
fi

echo "✓ lint/test tienen implementación real."
