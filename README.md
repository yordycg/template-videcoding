# <Nombre del proyecto>

<!-- Cómo lucirá el proyecto terminado. Sustituye el bloque por la descripción real. -->

> **Vista final del producto:** una o dos frases del producto terminado, el problema que resuelve y para quién.

## Características

- [ ] F-01: <nombre>
- [ ] F-02: <nombre>

## Requisitos

<!-- Stack y dependencias del sistema. -->

## Instalación

```bash
# ...
```

## Uso

```bash
# ...
```

## Worktrees

Una tarea, un worktree: `~/.herdr/worktrees/<repo>/agent/<slug>`, nunca dos
agentes escribiendo en el mismo checkout.

`just install-hooks` instala `pre-commit` (los gates) y `post-checkout`, que
llama a `~/.local/bin/worktree-bootstrap` al crear un worktree enlazado: copia
los `.env` ignorados, instala las dependencias del stack y ejecuta
`.herdr/worktree-bootstrap.sh` si existe.

Sin el helper global, `post-checkout` no hace nada y `git worktree add` sigue
funcionando. Si el bootstrap falla, se repite a mano:

```bash
~/.local/bin/worktree-bootstrap --force "$PWD"
```

## Roadmap

Ver [`docs/roadmap.md`](./docs/roadmap.md) y el seguimiento de tareas en [`tasks.yaml`](./tasks.yaml) / [`TASKS.md`](./TASKS.md).
