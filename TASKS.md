# TASKS.md — Seguimiento de Tareas

> Vista generada automáticamente a partir de `tasks.yaml` (SSOT).
> **No edites este archivo a mano.** Usa `just task <cmd>` o edita `tasks.yaml`.

**Progreso general:** `[░░░░░░░░░░░░░░░░░░░░] 0% (0/4)`

| Estado | Cantidad | Descripción |
|---|---|---|
| 🟢 **Hechas** | 0 | Verificadas por el humano |
| 🔵 **En revisión** | 0 | Terminadas por el worker, listas para verificar |
| 🟠 **En curso** | 0 | En desarrollo activo (WIP=1) |
| 🔴 **To Do** | 1 | Aprobadas y desbloqueadas, listas para tomar |
| ⬜ **Bloqueadas** | 2 | Esperando dependencias no completadas |
| 🟣 **Propuestas** | 1 | Propuestas, esperando aprobación |

---

## Detalle de Tareas por Fase

### Fase / Ola 0

| ID | Estado | Área | Título | Dependencias |
|---|---|---|---|---|
| `SETUP-01` | 🔴 to_do | Setup | Bootstrap del proyecto y estructura inicial | *(ninguna)* |
| `SETUP-02` | ⬜ blocked | Setup | Estructura de carpetas y configuración de entorno | `SETUP-01` |
| `SETUP-03` | ⬜ blocked | Setup | Fijar .agents/codestyle.md y ejemplo de estilo heredado | `SETUP-02` |

### Fase / Ola 1

| ID | Estado | Área | Título | Dependencias |
|---|---|---|---|---|
| `FEAT-01` | 🟣 proposed | Core | Primera feature / spike de dominio con TDD | `SETUP-03` |

---

## Grafo de Dependencias (Mermaid)

```mermaid
flowchart TD
  subgraph Ola_0["Ola 0"]
    SETUP-01["SETUP-01: Bootstrap del proyecto y estructura inicial"]
    SETUP-02["SETUP-02: Estructura de carpetas y configuración de entorno"]
    SETUP-03["SETUP-03: Fijar .agents/codestyle.md y ejemplo de estilo heredado"]
  end
  subgraph Ola_1["Ola 1"]
    FEAT-01["FEAT-01: Primera feature / spike de dominio con TDD"]
  end

  SETUP-01 --> SETUP-02
  SETUP-02 --> SETUP-03
  SETUP-03 --> FEAT-01

  classDef done fill:#22c55e,stroke:#15803d,color:#fff,stroke-width:2px;
  classDef doing fill:#f97316,stroke:#c2410c,color:#fff,stroke-width:2px;
  classDef review fill:#06b6d4,stroke:#0e7490,color:#fff,stroke-width:2px;
  classDef todo fill:#ef4444,stroke:#b91c1c,color:#fff,stroke-width:2px;
  classDef blocked fill:#64748b,stroke:#475569,color:#fff,stroke-width:1px;
  classDef proposed fill:#a855f7,stroke:#7e22ce,color:#fff,stroke-width:1px;

  class SETUP-01 todo;
  class SETUP-02,SETUP-03 blocked;
  class FEAT-01 proposed;
```
