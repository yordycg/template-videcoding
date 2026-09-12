# Fase 6 — Pruebas y Control de Calidad (Testing & QA)

**Proyecto**: [Nombre del proyecto]
**Tamaño del proyecto**: [ ] Chico &nbsp; [ ] Mediano &nbsp; [ ] Grande

> **Nivel de detalle según tamaño** (Guía de Escalamiento):
> - **Chico**: camino feliz + 2-3 casos de error a mano.
> - **Mediano**: camino feliz + destructivas + 3-5 unit tests en lo crítico.
> - **Grande**: suite de tests + rendimiento con datos reales.

---

## 1. Pruebas de Camino Feliz (Happy Path)

| # | Escenario | Datos de entrada | Resultado esperado | Resultado obtenido | ✅/❌ |
|---|---|---|---|---|---|
| 1 | [caso normal] | [datos] | [esperado] | [obtenido] | |
| 2 | [caso normal] | [datos] | [esperado] | [obtenido] | |

---

## 2. Pruebas con Datos Destructivos / Erróneos

*(Mediano y Grande — en Chico basta con 2-3 casos "a mano" sin tabla formal)*

| # | Escenario | Qué se prueba | Resultado esperado | ✅/❌ |
|---|---|---|---|---|
| 1 | Valores nulos | [campo] | [mensaje de error claro, no crash] | |
| 2 | Textos gigantes | [campo] | [validación/truncamiento] | |
| 3 | Formatos incorrectos | [campo] | [rechazo con mensaje claro] | |
| 4 | Corte de conexión a mitad de ejecución | [operación] | [rollback / reintento] | |

---

## 3. Unit Tests en funciones críticas

*(Mediano: 3-5 tests · Grande: suite completa)*

| Función | Caso de test | Resultado esperado | ✅/❌ |
|---|---|---|---|
| [nombre_funcion] | [caso 1] | [esperado] | |
| [nombre_funcion] | [caso 2] | [esperado] | |

---

## 4. Pruebas de Rendimiento

*(Solo Grande — en Mediano opcional si el volumen de datos es incierto)*

| Volumen de datos | Tiempo de respuesta esperado | Tiempo obtenido | ✅/❌ |
|---|---|---|---|
| 10 registros | [tiempo] | [tiempo] | |
| 10,000 registros | [tiempo] | [tiempo] | |

---

## Preguntas de autochequeo

- [ ] ¿Qué pasa si el usuario ingresa un dato inválido? — Cubierto en tabla de datos destructivos
- [ ] ¿El programa muestra un mensaje de error claro, o se cae con una excepción incomprensible?

## Checklist de cierre de Fase 6

- [ ] Camino feliz probado
- [ ] Casos destructivos probados *(según tamaño)*
- [ ] Unit tests en funciones críticas *(según tamaño)*
- [ ] Rendimiento probado *(si aplica)*
