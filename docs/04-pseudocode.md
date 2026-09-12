# Fase 4 — Diseño Lógico y Pseudocódigo

**Proyecto**: [Nombre del proyecto]
**Tamaño del proyecto**: [ ] Chico &nbsp; [ ] Mediano &nbsp; [ ] Grande

> **Nivel de detalle según tamaño** (Guía de Escalamiento):
> - **Chico**: solo el flujo principal, 10-15 líneas.
> - **Mediano**: flujo principal + 2-3 funciones críticas.
> - **Grande**: todas las funciones no triviales.

> Objetivo: resolver la lógica pesada y los algoritmos en español/inglés simple, antes de la sintaxis estricta del lenguaje.

---

## 1. Pseudocódigo — Flujo Principal

```
INICIO
    [PASO 1]
    [PASO 2]
    SI [condición] NO se cumple:
        [manejo de error]
    SINO:
        [continuación del flujo]
FIN
```

---

## 2. Funciones críticas

*(Solo Mediano/Grande — agregar un bloque por cada función no trivial)*

### Función: [nombre_funcion]

**Propósito**: [qué resuelve]

```
FUNCION nombre_funcion(parametros)
    [lógica paso a paso en español]
    RETORNAR [resultado]
FIN FUNCION
```

---

## 3. Manejo de Casos de Borde y Errores

| Escenario | Qué debe pasar | Mensaje al usuario |
|---|---|---|
| [Ej: la API externa no responde] | [reintento / log / abortar] | [mensaje claro, no stacktrace] |
| [Ej: dato nulo o vacío] | [validación previa] | [mensaje claro] |
| [Ej: se corta la conexión a mitad de ejecución] | [rollback / guardado parcial] | [mensaje claro] |

---

## 4. Estructura de Carpetas y Módulos

```
proyecto/
├── src/
│   ├── [módulo1]/
│   └── [módulo2]/
├── tests/
├── docs/
└── meta/
```

---

## Preguntas de autochequeo antes de pasar a Fase 5

- [ ] ¿Qué pasa si la red falla, la API está caída o la página cambió su estructura? — Respondido arriba
- [ ] ¿Cómo se manejan los errores sin romper todo el programa? — Respondido arriba
- [ ] ¿Esta lógica es fácil de entender si la leo dentro de 6 meses?
- [ ] ¿Puedo explicar este pseudocódigo a alguien no técnico en 2 minutos?
