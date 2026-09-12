# TASKS.md — Seguimiento de tareas

> Espejo en markdown del tablero `Project.canvas` (Kanvas). **Deben estar SIEMPRE sincronizados** (dual-write): cada cambio de estado se refleja en ambos sitios en el mismo commit. Si divergen: `just sync-tracking`.

## Estados

| Estado | `TASKS.md` | Canvas | Quién |
|--------|-----------|--------|-------|
| Propuesta | `- [ ]` en "Propuestas" | 🟣 Purple | agente propone |
| Aprobada / To Do | `- [ ]` en "Pendientes" | 🔴 Red | humano aprueba |
| En curso | `- [ ]` + `— ▶ en curso` | 🟠 Orange | agente `start` |
| En revisión | `- [ ]` + `— 🔵 en revisión` | 🔵 Cyan | agente `finish` |
| Hecha | `- [x]` en "Hechas" | 🟢 Green | humano verifica |

---

## Pendientes (🔴 aprobadas)

### Setup
- [ ] `SETUP-01` Bootstrap del proyecto
- [ ] `SETUP-02` Estructura de carpetas
- [ ] `SETUP-03` Fijar CODESTYLE.md

### <Área>
- [ ] `API-01` <tarea> — *depende de SETUP-01*

---

## En curso (🟠 orange)

- (ninguna)

## En revisión (🔵 cyan)

- (ninguna)

## Hechas (🟢 green)

- (ninguna)

## Propuestas (🟣 purple, esperando aprobación)

- (ninguna)
