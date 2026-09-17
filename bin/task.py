#!/usr/bin/env python3
"""
bin/task.py — Motor SSOT de gestión de tareas con dependencias (DAG) para videcoding.
Zero dependencies: corre con Python 3 standard library.
"""

import argparse
import os
import re
import sys
from collections import defaultdict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YAML_FILE = os.path.join(PROJECT_ROOT, "tasks.yaml")
TASKS_MD = os.path.join(PROJECT_ROOT, "TASKS.md")

# Estados válidos
PROPOSED = "proposed"
BLOCKED = "blocked"
TODO = "to_do"
DOING = "doing"
REVIEW = "review"
DONE = "done"

VALID_STATES = {PROPOSED, BLOCKED, TODO, DOING, REVIEW, DONE}

STATE_EMOJI = {
    PROPOSED: "🟣",
    BLOCKED: "⬜",
    TODO: "🔴",
    DOING: "🟠",
    REVIEW: "🔵",
    DONE: "🟢",
}

STATE_LABEL = {
    PROPOSED: "Propuesta",
    BLOCKED: "Bloqueada",
    TODO: "To Do (lista)",
    DOING: "En curso",
    REVIEW: "En revisión",
    DONE: "Hecha",
}

# ---------------------------------------------------------------------------
# Zero-Dep YAML Parser & Serializer
# ---------------------------------------------------------------------------


def load_tasks(filepath=YAML_FILE):
    if not os.path.isfile(filepath):
        print(f"Error: {filepath} no existe.", file=sys.stderr)
        sys.exit(1)

    tasks = []
    cur_task = None
    in_desc = False
    desc_lines = []

    with open(filepath, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\r\n")
            stripped = line.strip()

            if in_desc:
                if line.startswith("      "):
                    desc_lines.append(line[6:])
                    continue
                elif not stripped:
                    desc_lines.append("")
                    continue
                else:
                    cur_task["desc"] = "\n".join(desc_lines).strip()
                    in_desc = False
                    desc_lines = []

            if not stripped or stripped.startswith("#"):
                continue

            if stripped.startswith("- id:"):
                if cur_task:
                    tasks.append(cur_task)
                cur_task = {
                    "id": stripped[5:].strip().strip("\"'"),
                    "depends_on": [],
                    "desc": "",
                    "phase": 0,
                    "area": "",
                    "status": PROPOSED,
                }
                continue

            if not cur_task:
                continue

            if stripped.startswith("title:"):
                cur_task["title"] = stripped[6:].strip().strip("\"'")
            elif stripped.startswith("area:"):
                cur_task["area"] = stripped[5:].strip().strip("\"'")
            elif stripped.startswith("phase:"):
                val = stripped[6:].strip()
                cur_task["phase"] = int(val) if val.isdigit() else val
            elif stripped.startswith("status:"):
                cur_task["status"] = (
                    stripped[7:].split("#")[0].strip().strip("\"'")
                )
            elif stripped.startswith("depends_on:"):
                val = stripped[11:].strip()
                if val.startswith("[") and val.endswith("]"):
                    content = val[1:-1].strip()
                    cur_task["depends_on"] = [
                        d.strip().strip("\"'")
                        for d in content.split(",")
                        if d.strip()
                    ]
                else:
                    cur_task["depends_on"] = []
            elif stripped.startswith("desc:"):
                val = stripped[5:].strip()
                if val in ("|-", "|", ">-", ">"):
                    in_desc = True
                    desc_lines = []
                else:
                    cur_task["desc"] = val.strip("\"'")

        if in_desc and cur_task:
            cur_task["desc"] = "\n".join(desc_lines).strip()
        if cur_task:
            tasks.append(cur_task)

    return tasks


def save_tasks(tasks, filepath=YAML_FILE):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(
            "# tasks.yaml — Single Source of Truth para seguimiento de"
            " tareas\n"
        )
        f.write("# Administrado con 'just task <cmd>' o 'bin/task.py'\n")
        f.write("version: 1\n\n")
        f.write("tasks:\n")
        for t in tasks:
            f.write(f"  - id: {t['id']}\n")
            title_escaped = t.get("title", "").replace('"', '\\"')
            f.write(f'    title: "{title_escaped}"\n')
            f.write(f"    area: {t.get('area', '')}\n")
            f.write(f"    phase: {t.get('phase', 0)}\n")
            f.write(f"    status: {t.get('status', PROPOSED)}\n")
            deps = ", ".join(t.get("depends_on", []))
            f.write(f"    depends_on: [{deps}]\n")
            desc = t.get("desc", "").strip()
            if "\n" in desc:
                f.write("    desc: |-\n")
                for line in desc.splitlines():
                    f.write(f"      {line}\n")
            else:
                desc_escaped = desc.replace('"', '\\"')
                f.write(f'    desc: "{desc_escaped}"\n')
            f.write("\n")


# ---------------------------------------------------------------------------
# DAG Algorithms: Cycles & Normalization
# ---------------------------------------------------------------------------


def find_cycle(tasks):
    adj = {t["id"]: t.get("depends_on", []) for t in tasks}
    visited = {}  # 0: unvisited, 1: visiting, 2: visited

    def dfs(node, path):
        visited[node] = 1
        for neighbor in adj.get(node, []):
            if neighbor not in adj:
                continue
            if visited.get(neighbor) == 1:
                idx = path.index(neighbor) if neighbor in path else 0
                return path[idx:] + [neighbor]
            if visited.get(neighbor) == 0 or neighbor not in visited:
                res = dfs(neighbor, path + [neighbor])
                if res:
                    return res
        visited[node] = 2
        return None

    for t in tasks:
        tid = t["id"]
        if visited.get(tid) != 2:
            cycle = dfs(tid, [tid])
            if cycle:
                return cycle
    return None


def normalize_states(tasks):
    task_map = {t["id"]: t for t in tasks}
    changed = False

    for t in tasks:
        # Solo normalizamos tareas aprobadas que no están activas ni terminadas
        if t["status"] in (TODO, BLOCKED):
            deps = t.get("depends_on", [])
            all_done = all(
                task_map.get(d) and task_map[d]["status"] == DONE for d in deps
            )
            new_status = TODO if all_done else BLOCKED
            if t["status"] != new_status:
                t["status"] = new_status
                changed = True

    return changed


# ---------------------------------------------------------------------------
# Render TASKS.md & Mermaid
# ---------------------------------------------------------------------------


def render_markdown(tasks, filepath=TASKS_MD):
    task_map = {t["id"]: t for t in tasks}
    total = len(tasks)
    counts = defaultdict(int)
    for t in tasks:
        counts[t["status"]] += 1

    pct = int((counts[DONE] / total) * 100) if total > 0 else 0
    filled = int(pct / 5)
    bar = "█" * filled + "░" * (20 - filled)

    lines = []
    lines.append("# TASKS.md — Seguimiento de Tareas")
    lines.append("")
    lines.append(
        "> Vista generada automáticamente a partir de `tasks.yaml` (SSOT)."
    )
    lines.append(
        "> **No edites este archivo a mano.** Usa `just task <cmd>` o edita"
        " `tasks.yaml`."
    )
    lines.append("")
    lines.append(f"**Progreso general:** `[{bar}] {pct}% ({counts[DONE]}/{total})`")
    lines.append("")
    lines.append("| Estado | Cantidad | Descripción |")
    lines.append("|---|---|---|")
    lines.append(
        f"| 🟢 **Hechas** | {counts[DONE]} | Verificadas por el humano |"
    )
    lines.append(
        f"| 🔵 **En revisión** | {counts[REVIEW]} | Terminadas por el worker,"
        " listas para verificar |"
    )
    lines.append(
        f"| 🟠 **En curso** | {counts[DOING]} | En desarrollo activo (WIP=1) |"
    )
    lines.append(
        f"| 🔴 **To Do** | {counts[TODO]} | Aprobadas y desbloqueadas, listas para"
        " tomar |"
    )
    lines.append(
        f"| ⬜ **Bloqueadas** | {counts[BLOCKED]} | Esperando dependencias no"
        " completadas |"
    )
    lines.append(
        f"| 🟣 **Propuestas** | {counts[PROPOSED]} | Propuestas, esperando"
        " aprobación |"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Agrupar por fase
    phases = defaultdict(list)
    for t in tasks:
        phases[t.get("phase", 0)].append(t)

    lines.append("## Detalle de Tareas por Fase")
    lines.append("")

    for phase_num in sorted(phases.keys()):
        phase_tasks = phases[phase_num]
        lines.append(f"### Fase / Ola {phase_num}")
        lines.append("")
        lines.append(
            "| ID | Estado | Área | Título | Dependencias |"
        )
        lines.append("|---|---|---|---|---|")
        for t in phase_tasks:
            emoji = STATE_EMOJI.get(t["status"], "❓")
            deps_str = (
                ", ".join(f"`{d}`" for d in t.get("depends_on", []))
                if t.get("depends_on")
                else "*(ninguna)*"
            )
            lines.append(
                f"| `{t['id']}` | {emoji} {t['status']} | {t.get('area','')} |"
                f" {t['title']} | {deps_str} |"
            )
        lines.append("")

    # Diagrama Mermaid
    lines.append("---")
    lines.append("")
    lines.append("## Grafo de Dependencias (Mermaid)")
    lines.append("")
    lines.append("```mermaid")
    lines.append("flowchart TD")

    # Subgrafos por fase
    for phase_num in sorted(phases.keys()):
        phase_tasks = phases[phase_num]
        lines.append(f'  subgraph Ola_{phase_num}["Ola {phase_num}"]')
        for t in phase_tasks:
            clean_title = (
                t["title"].replace('"', "'").replace("[", "(").replace("]", ")")
            )
            lines.append(f'    {t["id"]}["{t["id"]}: {clean_title}"]')
        lines.append("  end")

    # Aristas
    lines.append("")
    for t in tasks:
        for d in t.get("depends_on", []):
            lines.append(f"  {d} --> {t['id']}")

    lines.append("")
    lines.append(
        "  classDef done fill:#22c55e,stroke:#15803d,color:#fff,stroke-width:2px;"
    )
    lines.append(
        "  classDef doing"
        " fill:#f97316,stroke:#c2410c,color:#fff,stroke-width:2px;"
    )
    lines.append(
        "  classDef review"
        " fill:#06b6d4,stroke:#0e7490,color:#fff,stroke-width:2px;"
    )
    lines.append(
        "  classDef todo"
        " fill:#ef4444,stroke:#b91c1c,color:#fff,stroke-width:2px;"
    )
    lines.append(
        "  classDef blocked"
        " fill:#64748b,stroke:#475569,color:#fff,stroke-width:1px;"
    )
    lines.append(
        "  classDef proposed"
        " fill:#a855f7,stroke:#7e22ce,color:#fff,stroke-width:1px;"
    )
    lines.append("")

    for state, cls in [
        (DONE, "done"),
        (DOING, "doing"),
        (REVIEW, "review"),
        (TODO, "todo"),
        (BLOCKED, "blocked"),
        (PROPOSED, "proposed"),
    ]:
        ids = [t["id"] for t in tasks if t["status"] == state]
        if ids:
            lines.append(f"  class {','.join(ids)} {cls};")

    lines.append("```")
    lines.append("")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ---------------------------------------------------------------------------
# CLI Commands
# ---------------------------------------------------------------------------


def cmd_status(tasks, _args):
    total = len(tasks)
    counts = defaultdict(int)
    for t in tasks:
        counts[t["status"]] += 1

    pct = int((counts[DONE] / total) * 100) if total > 0 else 0
    filled = int(pct / 5)
    bar = "█" * filled + "░" * (20 - filled)

    project_name = os.path.basename(PROJECT_ROOT)
    print(f"\n[{project_name}] {total} tareas | Progreso: [{bar}] {pct}%")
    print(
        f"  🟢 {counts[DONE]} hechas  |  🔵 {counts[REVIEW]} revisión  |  🟠"
        f" {counts[DOING]} en curso"
    )
    print(
        f"  🔴 {counts[TODO]} listas  |  ⬜ {counts[BLOCKED]} bloqueadas  |  🟣"
        f" {counts[PROPOSED]} propuestas\n"
    )

    doing = [t for t in tasks if t["status"] == DOING]
    if doing:
        print("▶ EN CURSO (WIP=1):")
        for t in doing:
            print(f"  {t['id']} [{t.get('area', '')}] {t['title']}")
        print()

    review = [t for t in tasks if t["status"] == REVIEW]
    if review:
        print("🔵 EN REVISIÓN (esperando verificación humana):")
        for t in review:
            print(f"  {t['id']} [{t.get('area', '')}] {t['title']}")
        print()

    ready = [t for t in tasks if t["status"] == TODO]
    if ready:
        print("🔴 LISTAS PARA TOMAR (desbloqueadas):")
        for t in ready[:10]:
            print(f"  {t['id']} [{t.get('area', '')}] {t['title']}")
        if len(ready) > 10:
            print(f"  ... y {len(ready) - 10} tareas más (usa 'task ready').")
        print()


def cmd_ready(tasks, _args):
    normalize_states(tasks)
    ready = [t for t in tasks if t["status"] == TODO]
    if not ready:
        print("No hay tareas listas para tomar.")
        return
    print(f"Tareas listas para tomar ({len(ready)}):")
    for t in ready:
        deps = (
            f"(deps: {', '.join(t['depends_on'])})" if t["depends_on"] else ""
        )
        print(f"  {t['id']:<8} [{t.get('area', ''):<12}] {t['title']} {deps}")


def cmd_list(tasks, args):
    filtered = tasks
    if args.status:
        filtered = [
            t for t in filtered if t["status"].lower() == args.status.lower()
        ]
    if args.area:
        filtered = [
            t
            for t in filtered
            if t.get("area", "").lower() == args.area.lower()
        ]
    if args.phase is not None:
        filtered = [t for t in filtered if str(t.get("phase")) == str(args.phase)]

    if not filtered:
        print("No se encontraron tareas con los filtros especificados.")
        return

    print(f"{'ID':<8} {'Estado':<12} {'Fase':<5} {'Área':<14} {'Título'}")
    print("-" * 75)
    for t in filtered:
        print(
            f"{t['id']:<8} {t['status']:<12} {t.get('phase', 0):<5}"
            f" {t.get('area', ''):<14} {t['title']}"
        )


def cmd_show(tasks, args):
    tid = args.id.upper()
    task = next((t for t in tasks if t["id"].upper() == tid), None)
    if not task:
        print(f"Error: Tarea '{args.id}' no encontrada.", file=sys.stderr)
        sys.exit(1)

    task_map = {t["id"]: t for t in tasks}
    dependents = [t for t in tasks if task["id"] in t.get("depends_on", [])]

    print(f"\nID:          {task['id']}")
    print(f"Título:      {task['title']}")
    print(f"Área:        {task.get('area', '')}")
    print(f"Fase:        {task.get('phase', 0)}")
    print(
        f"Estado:      {STATE_EMOJI.get(task['status'], '')} {task['status']}"
    )
    print("\nDependencias (bloquean a esta tarea):")
    if task.get("depends_on"):
        for d in task["depends_on"]:
            d_task = task_map.get(d)
            st = d_task["status"] if d_task else "INEXISTENTE"
            em = STATE_EMOJI.get(st, "❓")
            print(f"  - {d} [{em} {st}] {d_task['title'] if d_task else ''}")
    else:
        print("  (ninguna)")

    print("\nDependientes (esta tarea las bloquea):")
    if dependents:
        for dep in dependents:
            em = STATE_EMOJI.get(dep["status"], "❓")
            print(f"  - {dep['id']} [{em} {dep['status']}] {dep['title']}")
    else:
        print("  (ninguna)")

    print(f"\nDescripción:\n{task.get('desc', '(sin descripción)')}\n")


def cmd_start(tasks, args):
    tid = args.id.upper()
    task = next((t for t in tasks if t["id"].upper() == tid), None)
    if not task:
        print(f"Error: Tarea '{args.id}' no encontrada.", file=sys.stderr)
        sys.exit(1)

    # Regla WIP=1: verificar si ya hay otra en curso
    other_doing = [
        t for t in tasks if t["status"] == DOING and t["id"] != task["id"]
    ]
    if other_doing:
        print(
            f"Error (WIP=1): Ya está en curso la tarea '{other_doing[0]['id']}'"
            f" ({other_doing[0]['title']}).",
            file=sys.stderr,
        )
        print("Finalízala o paúsala antes de iniciar otra.", file=sys.stderr)
        sys.exit(1)

    # Verificar que esté en to_do
    if task["status"] != TODO:
        print(
            f"Error: No se puede iniciar '{task['id']}' porque está en estado"
            f" '{task['status']}' (debe estar en 'to_do').",
            file=sys.stderr,
        )
        sys.exit(1)

    # Verificar dependencias
    task_map = {t["id"]: t for t in tasks}
    for d in task.get("depends_on", []):
        if not task_map.get(d) or task_map[d]["status"] != DONE:
            print(
                f"Error: La dependencia '{d}' no está terminada ('done').",
                file=sys.stderr,
            )
            sys.exit(1)

    task["status"] = DOING
    save_tasks(tasks)
    render_markdown(tasks)
    print(f"✓ Tarea '{task['id']}' iniciada (to_do -> doing). Vistas actualizadas.")


def cmd_finish(tasks, args):
    tid = args.id.upper()
    task = next((t for t in tasks if t["id"].upper() == tid), None)
    if not task:
        print(f"Error: Tarea '{args.id}' no encontrada.", file=sys.stderr)
        sys.exit(1)

    if task["status"] != DOING:
        print(
            f"Error: Tarea '{task['id']}' está en estado '{task['status']}'"
            " (debe estar en 'doing').",
            file=sys.stderr,
        )
        sys.exit(1)

    task["status"] = REVIEW
    save_tasks(tasks)
    render_markdown(tasks)
    print(
        f"✓ Tarea '{task['id']}' lista para revisión (doing -> review). Vistas"
        " actualizadas."
    )


def cmd_pause(tasks, args):
    tid = args.id.upper()
    task = next((t for t in tasks if t["id"].upper() == tid), None)
    if not task:
        print(f"Error: Tarea '{args.id}' no encontrada.", file=sys.stderr)
        sys.exit(1)

    if task["status"] != DOING:
        print(
            f"Error: Tarea '{task['id']}' no está en curso ('doing').",
            file=sys.stderr,
        )
        sys.exit(1)

    task["status"] = TODO
    save_tasks(tasks)
    render_markdown(tasks)
    print(
        f"✓ Tarea '{task['id']}' pausada (doing -> to_do). Vistas actualizadas."
    )


def cmd_approve(tasks, args):
    task_map = {t["id"].upper(): t for t in tasks}
    approved_count = 0

    for raw_id in args.ids:
        tid = raw_id.upper()
        task = task_map.get(tid)
        if not task:
            print(f"Aviso: Tarea '{raw_id}' no encontrada.", file=sys.stderr)
            continue
        if task["status"] != PROPOSED:
            print(
                f"Aviso: Tarea '{task['id']}' ya no está en 'proposed'"
                f" (está en '{task['status']}').",
                file=sys.stderr,
            )
            continue

        # Verificar dependencias para saber si queda to_do o blocked
        all_done = all(
            task_map.get(d.upper())
            and task_map[d.upper()]["status"] == DONE
            for d in task.get("depends_on", [])
        )
        task["status"] = TODO if all_done else BLOCKED
        approved_count += 1
        print(f"✓ Tarea '{task['id']}' aprobada -> '{task['status']}'.")

    if approved_count > 0:
        normalize_states(tasks)
        save_tasks(tasks)
        render_markdown(tasks)
        print(f"✓ {approved_count} tarea(s) aprobada(s). Vistas actualizadas.")


def cmd_verify(tasks, args):
    tid = args.id.upper()
    task = next((t for t in tasks if t["id"].upper() == tid), None)
    if not task:
        print(f"Error: Tarea '{args.id}' no encontrada.", file=sys.stderr)
        sys.exit(1)

    if task["status"] != REVIEW:
        print(
            f"Error: Tarea '{task['id']}' está en estado '{task['status']}'"
            " (debe estar en 'review').",
            file=sys.stderr,
        )
        sys.exit(1)

    task["status"] = DONE
    unblocked = []
    # Cascada de desbloqueo: evaluar tareas dependientes
    normalize_states(tasks)

    # Identificar cuáles pasaron a to_do
    for t in tasks:
        if t["status"] == TODO and task["id"] in t.get("depends_on", []):
            unblocked.append(t["id"])

    save_tasks(tasks)
    render_markdown(tasks)
    print(f"✓ Tarea '{task['id']}' verificada (review -> done).")
    if unblocked:
        print(f"  → Tareas desbloqueadas automáticamente: {', '.join(unblocked)}")
    print("Vistas actualizadas.")


def cmd_check(tasks, _args):
    # 1. Validar unicidad de IDs
    seen = set()
    for t in tasks:
        tid = t.get("id")
        if not tid:
            print("Error: Existe una tarea sin ID.", file=sys.stderr)
            sys.exit(1)
        if tid in seen:
            print(f"Error: ID duplicado '{tid}'.", file=sys.stderr)
            sys.exit(1)
        seen.add(tid)

    # 2. Validar estados
    for t in tasks:
        st = t.get("status")
        if st not in VALID_STATES:
            print(
                f"Error: Tarea '{t['id']}' tiene estado inválido '{st}'.",
                file=sys.stderr,
            )
            sys.exit(1)

    # 3. Validar dependencias existentes
    for t in tasks:
        for d in t.get("depends_on", []):
            if d not in seen:
                print(
                    f"Error: Tarea '{t['id']}' depende de '{d}', que no"
                    " existe.",
                    file=sys.stderr,
                )
                sys.exit(1)

    # 4. Validar ciclos
    cycle = find_cycle(tasks)
    if cycle:
        print(
            f"Error: Ciclo detectado en el grafo: {' -> '.join(cycle)}",
            file=sys.stderr,
        )
        sys.exit(1)

    # 5. Validar que ninguna tarea en to_do o doing tenga dependencias incompletas
    task_map = {t["id"]: t for t in tasks}
    for t in tasks:
        if t["status"] in (TODO, DOING):
            for d in t.get("depends_on", []):
                if task_map[d]["status"] != DONE:
                    print(
                        f"Error: Tarea '{t['id']}' está en '{t['status']}' pero"
                        f" su dependencia '{d}' no está 'done' (está en"
                        f" '{task_map[d]['status']}').",
                        file=sys.stderr,
                    )
                    sys.exit(1)

    print(f"✓ tasks.yaml OK ({len(tasks)} tareas verificadas sin ciclos).")


def cmd_render(tasks, _args):
    normalize_states(tasks)
    save_tasks(tasks)
    render_markdown(tasks)
    print(f"✓ TASKS.md regenerado a partir de {YAML_FILE}.")


# ---------------------------------------------------------------------------
# Main Router
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="CLI para gestión de tareas (SSOT tasks.yaml)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # status
    p_status = subparsers.add_parser("status", help="Resumen del tablero")
    p_status.set_defaults(func=cmd_status)

    # ready
    p_ready = subparsers.add_parser("ready", help="Tareas listas para tomar")
    p_ready.set_defaults(func=cmd_ready)

    # list
    p_list = subparsers.add_parser("list", help="Listado filtrable de tareas")
    p_list.add_argument("--status", help="Filtrar por estado")
    p_list.add_argument("--area", help="Filtrar por área")
    p_list.add_argument("--phase", help="Filtrar por fase")
    p_list.set_defaults(func=cmd_list)

    # show
    p_show = subparsers.add_parser("show", help="Detalle de una tarea")
    p_show.add_argument("id", help="ID de la tarea")
    p_show.set_defaults(func=cmd_show)

    # start
    p_start = subparsers.add_parser("start", help="Iniciar tarea (to_do -> doing)")
    p_start.add_argument("id", help="ID de la tarea")
    p_start.set_defaults(func=cmd_start)

    # finish
    p_finish = subparsers.add_parser(
        "finish", help="Terminar tarea (doing -> review)"
    )
    p_finish.add_argument("id", help="ID de la tarea")
    p_finish.set_defaults(func=cmd_finish)

    # pause
    p_pause = subparsers.add_parser(
        "pause", help="Pausar tarea (doing -> to_do)"
    )
    p_pause.add_argument("id", help="ID de la tarea")
    p_pause.set_defaults(func=cmd_pause)

    # approve
    p_approve = subparsers.add_parser(
        "approve", help="Aprobar tarea (proposed -> to_do/blocked)"
    )
    p_approve.add_argument("ids", nargs="+", help="ID(s) de tareas a aprobar")
    p_approve.set_defaults(func=cmd_approve)

    # verify
    p_verify = subparsers.add_parser(
        "verify", help="Verificar tarea (review -> done)"
    )
    p_verify.add_argument("id", help="ID de la tarea")
    p_verify.set_defaults(func=cmd_verify)

    # check
    p_check = subparsers.add_parser("check", help="Validar integridad del grafo")
    p_check.set_defaults(func=cmd_check)

    # render
    p_render = subparsers.add_parser("render", help="Regenerar TASKS.md")
    p_render.set_defaults(func=cmd_render)

    args = parser.parse_args()
    tasks = load_tasks()
    args.func(tasks, args)


if __name__ == "__main__":
    main()
