# ROADMAP.md — Plan de trabajo (tareas atómicas)

> El architect descompone el proyecto en tareas atómicas. Los workers las ejecutan **una a la vez** (WIP=1).
> Cada bullet es UNA tarea con ID único. Se refleja en `TASKS.md` y en el tablero `Project.canvas` (dependencias = flechas).
> Formato del ID: `<ÁREA>-<NN>` (ej. `SETUP-01`, `API-01`).

## Fase 0 — Setup y skeleton *(la ejecuta el ARCHITECT)*

- [ ] `SETUP-01` Bootstrap del proyecto: tooling, test runner, linter, Justfile (targets `lint`/`test`/`dev`).
- [ ] `SETUP-02` Estructura de carpetas + módulo vacío compilando con test de humo.
- [ ] `SETUP-03` Fijar `CODESTYLE.md` con el ejemplo de estilo heredado.

## Fase 1 — <área>

- [ ] `API-01` <tarea atómica> — *(depende de: SETUP-01)*

## Fase 2 — <área>

- [ ] `UI-01` <tarea atómica> — *(depende de: API-01)*

<!--
Reglas:
- Tarea atómica = se implementa en < 1 commit con su test.
- Dependencias: IDs que deben estar verdes antes de poder empezar.
- El worker propone tareas nuevas en el canvas (🟣 purple) para que el humano las apruebe; no las añade como hechas.
-->
