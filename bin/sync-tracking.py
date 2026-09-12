#!/usr/bin/env python3
"""sync-tracking.py — Reconciles TASKS.md with Project.canvas (dual-write).

The canvas is the source of truth for task state:
  - Green (done) on canvas  -> TASKS.md checkbox becomes [x] (auto-fix).
  - Not green on canvas     -> TASKS.md checkbox stays/becomes [ ] (auto-fix).
  - Orange -> "— ▶ en curso", Cyan -> "— 🔵 en revisión" markers synced.

Human-only rule is preserved: this script never sets a task green on the canvas.

Usage:
  python3 bin/sync-tracking.py            # apply fixes
  python3 bin/sync-tracking.py --check    # report only, exit 1 if divergence
"""

import json
import os
import re
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANVAS = "Project.canvas"
TASKS_FILE = "TASKS.md"

CHECK = "--check" in sys.argv

TASK_RE = re.compile(r"^(\s*-\s+\[([ xX])\]\s+`([A-Za-z]+-\d+)`)(.*)$")
MARKER_DOING = "— ▶ en curso"
MARKER_REVIEW = "— 🔵 en revisión"

COLOR = {
    "0": "gray",
    "1": "red",
    "2": "orange",
    "3": "yellow",
    "4": "green",
    "5": "cyan",
    "6": "purple",
}


def canvas_states():
    res = subprocess.run(
        ["python3", "canvas-tool.py", CANVAS, "dump"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        sys.stderr.write(f"ERROR: no se pudo leer {CANVAS}:\n{res.stderr}\n")
        sys.exit(2)
    data = json.loads(res.stdout)
    states = {}
    for node in data.get("nodes", []):
        text = (node.get("text") or "").strip()
        m = re.match(r"##\s+([A-Za-z]+-\d+)", text)
        if node.get("type") == "text" and m:
            states[m.group(1).upper()] = COLOR.get(node.get("color"), "unknown")
    return states


def target_line(indent, task_id, color, rest=""):
    """Builds the canonical TASKS.md line for a task in the given canvas color."""
    checked = "x" if color == "green" else " "
    if color == "orange":
        marker = MARKER_DOING
    elif color == "cyan":
        marker = MARKER_REVIEW
    else:
        marker = ""
    parts = [f"{indent}- [{checked}] `{task_id}`"]
    if marker:
        parts.append(marker)
    if rest:
        parts.append(rest)
    return " ".join(parts)


def diverges(checked, color, rest):
    """True if the TASKS.md line state doesn't match the canvas color."""
    is_done = checked.lower() == "x"
    want_done = color == "green"
    has_doing = MARKER_DOING in rest
    has_review = MARKER_REVIEW in rest
    want_doing = color == "orange"
    want_review = color == "cyan"
    return is_done != want_done or has_doing != want_doing or has_review != want_review


def main():
    states = canvas_states()
    if not states:
        print(f"→ {CANVAS} no tiene tareas aún. Nada que sincronizar.")
        return 0

    with open(os.path.join(PROJECT_ROOT, TASKS_FILE), encoding="utf-8") as f:
        lines = f.readlines()

    divergences = 0
    missing_in_tasks = set()
    fixed = 0
    output = []

    for line in lines:
        m = TASK_RE.match(line.rstrip("\n"))
        if not m:
            output.append(line)
            continue
        indent, checked, task_id, rest = m.groups()
        task_id = task_id.upper()
        color = states.get(task_id)
        if color is None:
            missing_in_tasks.add(task_id)
            output.append(line)
            continue
        if not diverges(checked, color, rest):
            output.append(line)
            continue
        divergences += 1
        if CHECK:
            output.append(line)
            continue
        rest_clean = rest.replace(MARKER_DOING, "").replace(MARKER_REVIEW, "").strip()
        indent_m = re.match(r"^(\s*)", line)
        indent = indent_m.group(1) if indent_m else ""
        output.append(target_line(indent, task_id, color, rest_clean) + "\n")
        fixed += 1

    # tasks on canvas but absent from TASKS.md
    on_canvas = set(states)
    tasks_in_file = {
        m.group(3).upper()
        for l in lines
        for m in [TASK_RE.match(l.rstrip())]
        if m is not None
    }
    missing_on_tasks = on_canvas - tasks_in_file - missing_in_tasks

    if CHECK:
        report = []
        if divergences:
            report.append(f"⚠  {divergences} divergencia(s) entre TASKS.md y {CANVAS}.")
        for tid in missing_on_tasks:
            report.append(f"⚠  Tarea en canvas pero no en TASKS.md: {tid} ({states[tid]}).")
        for tid in sorted(missing_in_tasks):
            report.append(f"⚠  Tarea en TASKS.md pero no en canvas: {tid}. Regístrala en el tablero.")
        if report:
            print("\n".join(report))
            return 1
        print("✓ TASKS.md y Project.canvas están sincronizados.")
        return 0

    if not CHECK and output:
        with open(os.path.join(PROJECT_ROOT, TASKS_FILE), "w", encoding="utf-8") as f:
            f.writelines(output)
        if divergences:
            print(f"→ Corregidas {fixed} línea(s) de TASKS.md según {CANVAS}.")
        else:
            print("→ TASKS.md ya estaba al día.")
    for tid in missing_on_tasks:
        print(f"⚠  Tarea en canvas pero no en TASKS.md: {tid} ({states[tid]}). Añádela a TASKS.md.")
    if missing_in_tasks:
        for tid in missing_in_tasks:
            print(f"⚠  Tarea en TASKS.md pero no en canvas: {tid}. Regístrala en el tablero.")
    print("✓ Sincronización completada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
