# Videcoding project — task runner
# Los workers corren `just lint` y `just test` ANTES de cada commit (gate).

default:
    @just --list

# --- Tracking (Kanvas + TASKS.md) ---

# Comprueba que el tablero está listo y muestra el estado
setup:
    #!/usr/bin/env bash
    set -euo pipefail
    test -f canvas-tool.py || { echo "Falta canvas-tool.py"; exit 1; }
    test -f Project.canvas || { echo "Falta Project.canvas"; exit 1; }
    python3 canvas-tool.py "Project.canvas" status
    echo "✓ Tablero OK. Ábrelo en Obsidian para el watcher plugin (opcional)."

status:
    python3 canvas-tool.py "Project.canvas" status

ready:
    python3 canvas-tool.py "Project.canvas" ready

# Reconciliar TASKS.md <-> Project.canvas (usar si divergen)
sync-tracking:
    #!/usr/bin/env bash
    set -euo pipefail
    python3 bin/sync-tracking.py

# Instalar el hook pre-commit que corre el gate
install-hooks:
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p .git/hooks
    cp bin/pre-commit .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    echo "✓ Hook pre-commit instalado."

# --- Calidad (gates) ---
# FASE 0: el architect sustituye los targets lint/test/dev por los reales del stack.

lint:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "⚠  FASE 0: define 'lint' en el Justfile (ruff, eslint, prettier --check...)."

test:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "⚠  FASE 0: define 'test' en el Justfile (pytest, vitest, go test...)."

# Gate completo pre-commit: lint + test + dual-write
gate:
    #!/usr/bin/env bash
    set -euo pipefail
    bash bin/gate.sh

dev:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "⚠  FASE 0: define 'dev' en el Justfile (uvicorn, vite, cargo run...)."
