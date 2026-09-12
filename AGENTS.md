# AGENTS.md — Videcoding Workflow (Architect + Workers)

Este proyecto se ejecuta con el flujo de **videcoding**: un **architect** (modelo potente) define las especificaciones y descompone el trabajo en tareas atómicas; los **workers** (modelo barato) las ejecutan una a una con **TDD estricto**. Este archivo es la fuente de verdad para **cualquier agente** (opencode, pi, claude, codex…): las reglas son agnósticas a la herramienta.

---

## 1. Fuentes de verdad (leer en este orden)

| # | Archivo | Contenido |
|---|---------|-----------|
| 1 | `SPECS.md` | Spec técnica: comportamiento esperado, entradas/salidas, casos borde. |
| 2 | `README.md` | Visión del proyecto terminado (producto final). |
| 3 | `CODESTYLE.md` | Reglas de estilo obligatorias para todo el código. |
| 4 | `ROADMAP.md` | Plan en tareas atómicas con fases y dependencias. |
| 5 | `TASKS.md` + `Project.canvas` | Tracking de ejecución. **Siempre sincronizados (dual-write).** |

**Regla:** no asumas nada que no esté en `SPECS.md`. Si una tarea necesita una decisión, pregúntala o documéntala (ADR liviano en `SPECS.md §7`) antes de codear.

---

## 2. Roles

### Architect (modelo potente)
- Genera/refina `SPECS.md`, `README.md`, `CODESTYLE.md` y `ROADMAP.md`.
- Descompone el proyecto en tareas atómicas (una tarea = un commit con test).
- Ejecuta la **Fase 0/1**: skeleton, tooling (test runner, linter), estructura y el ejemplo de estilo heredado.
- Revisa el trabajo de los workers cuando el humano lo pida.
- **No** implementa el grueso de las tareas: eso es trabajo del worker.

### Worker (modelo barato)
- Ejecuta **UNA tarea a la vez** (WIP=1).
- Lee **solo la sección relevante** de `SPECS.md` para su tarea (curse of instructions: más contexto = peor adherencia).
- Aplica **TDD estricto** y corre los **gates** antes de cada commit.
- Mantiene `TASKS.md` y `Project.canvas` sincronizados (**dual-write**).

---

## 3. TDD estricto (obligatorio, sin excepciones)

> Nada de código sin un test que falle primero. "Escribe tests que FALLEN, no implementes aún."

1. **RED** — escribe el test que falla (la feature no existe).
2. **GREEN** — implementa el mínimo para que pase.
3. **REFACTOR** — limpia manteniendo el verde.

Evidencia: el test falla **antes** de implementar y pasa **después**. `just test` en verde al terminar.

---

## 4. Gates (antes de CADA commit)

1. `just lint` → sin errores.
2. `just test` → sin errores.
3. Formatear el código antes de commitear.
4. `just gate` (o el hook pre-commit) verifica todo lo anterior + el dual-write.

---

## 5. No self-verify

El agente que escribe **no** se marca done:
- Termina y deja la tarea en **Review** (cian) → `python canvas-tool.py "Project.canvas" finish <ID>`.
- El **humano** revisa y pone el **verde** (done). Solo el humano.

---

## 6. Dual-write obligatorio (TASKS.md ↔ Project.canvas)

Cada cambio de estado de una tarea se refleja **en ambos sitios en el mismo commit**:

| Estado | `Project.canvas` (via CLI) | `TASKS.md` |
|--------|----------------------------|------------|
| Propuesta | `propose` (🟣) | `- [ ]` en sección "Propuestas" |
| Aprobada | humano la pone roja (🔴) | `- [ ]` en sección "Pendientes" |
| En curso | `start <ID>` (🟠) | `- [ ]` con marcador `— ▶ en curso` |
| En revisión | `finish <ID>` (🔵) | `- [ ]` con marcador `— 🔵 en revisión` |
| Hecha | **humano** la pone verde (🟢) | `- [x]` en sección "Hechas" |

- **Nunca** editar `Project.canvas` a mano: siempre vía `python canvas-tool.py "Project.canvas" <cmd>`.
- Si los estados divergen, ejecutar `just sync-tracking` antes de continuar.

---

## 7. Sesión típica del worker

1. `just status` → lee el board (canvas) y `TASKS.md`.
2. `just ready` → elige la tarea de mayor prioridad sin dependencias pendientes.
3. `python canvas-tool.py "Project.canvas" start <ID>` + marca `— ▶ en curso` en `TASKS.md`.
4. **TDD**: test rojo → implementación mínima → refactor. `just test` en verde.
5. Gates: `just lint` y `just test`. Formatear.
6. `python canvas-tool.py "Project.canvas" finish <ID>` + marca `— 🔵 en revisión` en `TASKS.md`.
7. Commit convencional (código + `TASKS.md` + `Project.canvas` juntos).
8. Reporta al humano: qué hizo, qué quedó pendiente, qué decide él.

---

## 8. Commits

- [Conventional Commits](https://www.conventionalcommits.org/) en inglés (`feat:`, `fix:`, `test:`, `docs:`, `chore:`).
- **Un checkpoint significativo = un commit.** El historial de git es el plan.
- No abusar de comentarios ni tokens: código autodocumentado (ver `CODESTYLE.md`).

---

## 9. Modelos y proveedores

| Rol | Modelo | Proveedor | Uso |
|-----|--------|-----------|-----|
| **Architect** | Claude Sonnet | OpenRouter (API key) | Spec, roadmap, Fase 0/1, review |
| **Worker** | DeepSeek | DeepSeek directo | Implementación con TDD estricto |
| **Scout** | Gemini Flash | Google | Exploración/investigación |

## 10. Notas por agente

### opencode
- Subagentes en `.opencode/agent/`: `architect` (Claude vía OpenRouter), `worker` (DeepSeek directo) y `scout` (Gemini).
- Cambia de agente con `Tab`. El agente predeterminado es el worker.
- El built-in `explore` usa Gemini (capa de exploración barata).

### pi
- Al iniciar en el proyecto, correr `/sdd-init` una vez (detecta stack y testing).
- El flujo SDD del Gentleman (`explore → proposal → spec → design → tasks → apply → verify → sync → archive`) se alinea con este workflow: `apply` = worker con TDD estricto, `verify` = gates.
- Asignar modelos por fase con `/gentle:models`: design=Claude (OpenRouter), implement=DeepSeek, explore=Gemini.
- Las reglas de este archivo son vinculantes igual que con opencode.
