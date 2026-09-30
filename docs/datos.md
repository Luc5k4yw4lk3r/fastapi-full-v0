# Datos de TaskFlow: frescura y ciclo de vida (s08)

Este documento describe, por entidad, **cada cuánto cambian** los datos (frescura) y su
**ciclo de vida**, y qué implicaciones tiene eso para un **agente** que los consume. No
hay IA/LLM en TaskFlow; "agente" acá es cualquier consumidor automatizado de la API que
necesita entender el estado del tablero.

## Frescura por entidad

| Entidad | Frecuencia de cambio | Notas |
|---|---|---|
| **Tarea** (estado) | **Alta** | El `estado` se mueve seguido (backlog → en progreso → hecho). Es el dato más volátil. |
| **Tarea** (título/descr.) | Media | Se edita al refinar la tarea; menos que el estado. |
| **Comentario** | Media/Alta | Se agregan durante la actividad; nunca se editan en el modelo actual. |
| **Responsable / Etiquetas** de una tarea | Media | Cambian al reasignar o reclasificar. |
| **Proyecto** | Baja | Nombre/descripción casi no cambian tras crearlo. |
| **Equipo** / membresías | Baja | Altas/bajas esporádicas. |
| **Usuario** | Muy baja | Datos de perfil estables. |

**Regla práctica para un agente:** lo que envejece rápido es el **estado de las tareas y
los comentarios**; el resto (proyecto, equipo, usuarios) puede considerarse casi estable
dentro de una sesión de trabajo.

## Ciclo de vida

- **Tarea:** se crea en `backlog` → avanza a `en progreso` → `hecho`. Hoy no se borran ni
  archivan (el borrado/archivado entra con el CRUD completo en s10). `created_at` marca el
  alta; `updated_at` se actualiza en cada cambio (p. ej. al mover de estado).
- **Comentario:** se crea asociado a una tarea y a un autor; es inmutable (append-only).
- **Proyecto / Equipo / Usuario / Etiqueta:** se crean y perduran; se editan rara vez.
- **Relaciones M:N** (usuario↔equipo, tarea↔etiqueta): se agregan/quitan sin afectar a las
  entidades en sí.

## Implicaciones para un agente que consume los datos

1. **Preferir lecturas autocontenidas.** El endpoint `GET /agent/proyectos/{id}/tablero`
   devuelve el proyecto con sus tareas agrupadas por columna y el contexto ya resuelto
   (responsable, etiquetas, comentarios). Así el agente entiende el tablero en **una sola
   llamada**, sin encadenar requests ni resolver ids.
2. **Usar la marca de frescura.** La respuesta incluye `generado_en` (UTC): indica el
   instante en que se armó la vista. Como el estado de las tareas cambia rápido, el agente
   debería **releer** antes de tomar decisiones si pasó un tiempo desde `generado_en`.
3. **Asumir estable lo de baja frescura.** Proyecto, equipo y usuarios pueden cachearse con
   tranquilidad durante una interacción; el estado de las tareas, no.
4. **Los comentarios son append-only:** un agente puede quedarse con los que ya leyó y solo
   traer los nuevos en la próxima lectura.

## Fuera de alcance (viene después)
- RAG / embeddings / búsqueda vectorial: **no** en TaskFlow.
- Endpoints de escritura (crear comentario, CRUD completo): **s10**.
- Versionado `/v1` del contrato: **s09** (por eso el endpoint de agentes va sin versionar
  por ahora).
