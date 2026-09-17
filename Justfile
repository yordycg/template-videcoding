# Videcoding project — task runner
# Los workers corren `just lint` y `just test` ANTES de cada commit (gate).

default:
    @just --list

# --- Tracking (SSOT tasks.yaml) ---

# Comprueba que el tablero está listo y muestra el estado
setup:
    #!/usr/bin/env bash
    set -euo pipefail
    test -f bin/task.py || { echo "Falta bin/task.py"; exit 1; }
    test -f tasks.yaml || { echo "Falta tasks.yaml"; exit 1; }
    if command -v opencode &>/dev/null; then
        mkdir -p .opencode
        ln -sfn ../.agents/agents .opencode/agent
    fi
    test -f .pi/settings.json || echo "⚠ Falta .pi/settings.json para aislamiento de skills."
    python3 bin/task.py status
    echo "✓ Tablero y entorno de agentes OK (OpenCode + Pi + Antigravity)."

status:
    python3 bin/task.py status

ready:
    python3 bin/task.py ready

# Wrapper directo para comandos de bin/task.py
task *ARGS:
    python3 bin/task.py {{ARGS}}

# Atajos para el ciclo de vida
start ID:
    python3 bin/task.py start {{ID}}

finish ID:
    python3 bin/task.py finish {{ID}}

approve +IDS:
    python3 bin/task.py approve {{IDS}}

verify ID:
    python3 bin/task.py verify {{ID}}

render:
    python3 bin/task.py render

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
