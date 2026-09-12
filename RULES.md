# RULES.md — Protocolo del tablero Kanvas (dual-write con TASKS.md)

Protocolo de gestión de tareas colaborativo entre el humano y los agentes usando un Canvas de Obsidian (`Project.canvas`) como tablero compartido. Adaptado del proyecto [XMihura/Kanvas](https://github.com/XMihura/Kanvas) (MIT) con la regla **dual-write** hacia `TASKS.md`.

---

## CRÍTICO: los agentes usan la CLI, nunca el JSON

**Los agentes NUNCA editan `.canvas` directamente.** Toda modificación pasa por la CLI, que fuerza las reglas (transiciones válidas, detección de ciclos, estados bloqueados):

```bash
python canvas-tool.py "Project.canvas" <command> [args]
```

La herramienta genera IDs, gestiona dependencias y colores. La edición directa del JSON está **prohibida**.

---

## Estados por color

| Color | Valor | Estado | Quién lo controla |
|-------|-------|--------|-------------------|
| Gris | `"0"` | **Bloqueada** — esperando dependencias | automático |
| Púrpura | `"6"` | **Propuesta** — sugerida por el agente | agente (`propose`/`batch`) |
| Rojo | `"1"` | **To Do** — aprobada y lista | humano |
| Naranja | `"2"` | **En curso** | agente (`start`) |
| Cian | `"5"` | **En revisión** — agente terminó | agente (`finish`) |
| Verde | `"4"` | **Hecha** — verificada | **solo humano** |

### Ciclo de vida
```
Propose (🟣) → Approve (🔴) → Start (🟠) → Finish (🔵) → Verify (🟢)
```

### Regla dual-write
Cada transición del canvas se refleja en `TASKS.md` en el **mismo commit** (ver tabla de estados en `TASKS.md`). El agente que escribe **no** pone verdes: deja en cian y el humano verifica.

---

## Lo que el agente PUEDE (vía CLI)

- **Leer:** `status`, `show <ID>`, `list`, `blocked`, `blocking`, `ready`, `dump`
- **Normalizar:** `normalize`
- **Proponer:** `propose <GRUPO> "<TITULO>" "<DESC>" [--depends-on ID ...]`, `propose-group`, `batch`
- **Ciclo:** `start <ID>` (rojo→naranja), `finish <ID>` (naranja→cian), `pause <ID>` (naranja→rojo)
- **Editar:** `edit <ID> "<texto>"` (solo tareas en curso)
- **Dependencias:** `add-dep <FROM> <TO>` (con detección de ciclos)

## Lo que el agente NO puede

- Editar `.canvas` directamente
- Marcar tarjetas verde (solo el humano)
- Trabajar tarjetas púrpura (propuestas sin aprobar), grises (bloqueadas) o cian (en revisión)
- Eliminar tarjetas o flechas, ni cambiar tarjetas verdes

---

## Sesión (protocolo)

1. **Inicio** — `python canvas-tool.py "Project.canvas" status` y `normalize` si hace falta.
2. **Elegir tarea** — `ready` → `show <ID>` → `start <ID>` (y marcar `— ▶ en curso` en `TASKS.md`).
3. **Trabajar** — TDD estricto (ver `AGENTS.md §3`); subtareas → `propose`; notas → `edit`.
4. **Terminar** — `finish <ID>` (cian) + marcar `— 🔵 en revisión` en `TASKS.md`. Informar al humano. NO poner verde.
5. **Repetir** — cuando el humano ponga verde: `normalize` → `ready`.
6. **Fin de sesión** — `status` y resumen.

---

## Referencia rápida de la CLI

| Comando | Descripción |
|---------|-------------|
| `status` | Resumen del tablero |
| `show <ID>` | Detalle de tarea con dependencias |
| `list [ESTADO\|GRUPO]` | Listar tareas (filtradas) |
| `ready` | Rojas con dependencias cumplidas |
| `blocked` | Grises y qué las bloquea |
| `start/finish/pause <ID>` | Ciclo de vida |
| `propose` / `propose-group` / `batch` | Proponer tareas/grupos |
| `edit <ID> "<TEXT>"` | Editar texto (naranja) |
| `add-dep <FROM> <TO>` | Añadir dependencia |
| `normalize` | Asignar IDs, arreglar bloqueos |

No hay `delete`, `done` ni `approve` para agentes: por diseño.
