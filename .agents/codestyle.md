# CODESTYLE.md — Reglas de estilo (obligatorias)

> Reglas para **todo** el código generado. El architect las define y refina en la Fase 0; los workers las cumplen siempre.

## Idioma

- Código, identificadores, nombres y mensajes de commit en **inglés**.
- La documentación de proyecto puede ser en el idioma del equipo.

## Principios

- **Depurable:** nombres descriptivos; lógica clara y trazable.
- **Comentarios:** solo técnicos y SOLO si aportan (explican el *porqué*, no el *qué*).
- **Formato:** siempre formateado antes de commitear (correr el formateador).
- **Estructura:** production-ready; separación de responsabilidades; sin código muerto ni código comentado.
- **Errores:** manejo explícito; nunca excepciones vacías; early returns para evitar anidamiento profundo.

## Prohibiciones

- Sin `TODO`/`FIXME` ni fragmentos incompletos: entregar código **funcional**.
- Sin secretos hardcodeados: usar `.env` (nunca comitear el `.env` real).

## Muestra de estilo (fijada por el architect en la Fase 0)

<!-- El architect reemplaza esto con UN ejemplo REAL de una función del proyecto, para que los workers hereden el estilo concreto. -->
