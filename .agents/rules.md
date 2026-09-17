# RULES.md — Protocolo de Gestión de Tareas (SSOT tasks.yaml)

Protocolo de gestión de tareas y dependencias para el flujo videcoding (Architect + Workers).
La **única fuente de verdad (SSOT)** es `tasks.yaml`. `TASKS.md` es una vista derivada generada automáticamente.

---

## 1. Comandos de Gestión de Tareas (`bin/task.py` / `just`)

Toda modificación de estado se realiza a través de `bin/task.py` o de los atajos del `Justfile`:

```bash
# Inspección
just status                # Panel compacto con métricas y tareas activas
just ready                 # Lista tareas desbloqueadas listas para tomar
python3 bin/task.py show <ID> # Detalle, bloqueadores y dependientes

# Ciclo del Worker
just start <ID>            # Pasa de to_do a doing (valida WIP=1 y dependencias)
just finish <ID>           # Pasa de doing a review (regenera vistas)

# Ciclo del Humano
just approve <ID> [...]    # Pasa de proposed a to_do (o blocked si tiene dependencias pendientes)
just verify <ID>           # Pasa de review a done (desbloquea en cascada las dependientes)

# Mantenimiento
just render                # Regenera TASKS.md con tablas y grafo Mermaid
python3 bin/task.py check  # Valida integridad (ausencia de ciclos, estados válidos)
```

---

## 2. Estados y Ciclo de Vida

| Estado | Emoj / Color | Quién lo controla | Significado |
|---|---|---|---|
| `proposed` | 🟣 Púrpura | Architect / Humano | Propuesta, esperando aprobación humana |
| `blocked` | ⬜ Gris | Automático (CLI) | Aprobada, pero con dependencias no completadas |
| `to_do` | 🔴 Rojo | Humano (`approve`) / Auto | Aprobada y desbloqueada, lista para que el worker la tome |
| `doing` | 🟠 Naranja | Worker (`start`) | En desarrollo activo (WIP=1 estricto) |
| `review` | 🔵 Cian | Worker (`finish`) | Implementación terminada, tests en verde, lista para verificación |
| `done` | 🟢 Verde | **Solo Humano** (`verify`) | Verificada por el humano; desbloquea tareas dependientes |

### Diagrama de Transición
```
        humano               auto (todas deps done)         worker                worker              humano
[proposed] ──────> [blocked] ─────────────────────> [to_do] ──────> [doing] ──────> [review] ──────> [done]
           approve                                          start                finish               verify
```

---

## 3. Reglas Estrictas

1. **WIP = 1**: Solo puede existir **una tarea en curso (`doing`) a la vez**. `just start` rechaza iniciar otra tarea si ya hay una activa.
2. **No self-verify**: El worker nunca se auto-aprueba ni se marca en verde (`done`). Su límite de ciclo es `just finish <ID>` (`review`). La verificación (`just verify <ID>`) es exclusividad humana.
3. **Desbloqueo en Cascada Automático**: Al correr `just verify <ID>`, el motor evalúa todas las tareas que estaban en `blocked` y pasan automáticamente a `to_do` si todas sus dependencias quedaron en `done`.
4. **Cero edición manual de vistas**: `TASKS.md` nunca se edita manualmente. Si se desea cambiar un título o descripción, se edita `tasks.yaml` o se ejecuta `just render`.
5. **Gates en Pre-commit**: `just gate` corre antes de cada commit verificando `lint`, `test` y `python3 bin/task.py check`.
