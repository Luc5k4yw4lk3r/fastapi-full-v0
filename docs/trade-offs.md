# Bitácora de trade-offs — TaskFlow

Registro de las decisiones de diseño del proyecto. **Antes** de cada decisión relevante
(almacenamiento, estructura, protocolo, modelado...) se presentan las alternativas; una
vez tomada, se anota acá con esta plantilla.

> Convención: una entrada por decisión, la más reciente arriba. Las decisiones de tipo
> arquitectónico más pesado (ej: elección de base de datos en s06) pueden escribirse
> como **ADR** siguiendo esta misma plantilla.

---

## Plantilla

```
### [sXX] Título corto de la decisión
- **Fecha:** AAAA-MM-DD
- **Decisión:** qué se decidió, en una frase.
- **Alternativas consideradas:**
  - Opción A — ...
  - Opción B — ...
  - Opción C — ...
- **Elección:** cuál se eligió.
- **Por qué:** justificación (patrones de acceso, simplicidad, alcance de la sesión...).
- **Consecuencias / a revisar más adelante:** (opcional)
```

---

### [s05] Representación de entidades sin ORM
- **Fecha:** 2026-09-30
- **Decisión:** modelar Tarea y Proyecto como clases Pydantic únicas, usadas tanto en el dominio como en el borde HTTP.
- **Alternativas consideradas:**
  - `@dataclass` de dominio + schemas Pydantic solo en el router — separa capas y desacopla el dominio del framework, pero exige mapear dominio ⇄ schema.
  - Pydantic para todo — una sola clase por entidad viaja de router a repository.
- **Elección:** Pydantic para todo.
- **Por qué:** menos código y menos mapeos para un prototipo; validación y serialización "gratis" con FastAPI.
- **Consecuencias / a revisar más adelante:** el dominio queda acoplado a Pydantic y el `id`/`estado` son campos del body de entrada (el server los ignora/forza). Si en s07 molesta el acoplamiento con la persistencia, podríamos introducir la separación dominio/schema entonces.

### [s05] Almacenamiento en memoria (capa repository)
- **Fecha:** 2026-09-30
- **Decisión:** guardar las tareas en un `dict[int, Tarea]` indexado por id.
- **Alternativas consideradas:**
  - `dict` indexado por id — buscar/actualizar/mover por id es O(1); listar es `values()`.
  - `list` — más intuitiva, pero buscar por id es O(n) y se aleja del acceso por clave de una BD.
- **Elección:** dict indexado por id.
- **Por qué:** modela mejor lo que después hará PostgreSQL (buscar por PK) y hace triviales las operaciones por id.
- **Consecuencias / a revisar más adelante:** el estado vive solo mientras corre el proceso; se pierde al reiniciar. La persistencia real llega en s07.

### [s05] Endpoint para mover el estado de una tarea
- **Fecha:** 2026-09-30
- **Decisión:** `POST /tasks/{id}/move` con body `{ "estado": "..." }` (estado validado por Enum).
- **Alternativas consideradas:**
  - `PATCH /tasks/{id}` — actualización parcial del recurso, semántica REST más "pura".
  - `POST /tasks/{id}/move` — endpoint de acción explícita (estilo RPC), verbo "mover" literal en la URL.
- **Elección:** POST .../move.
- **Por qué:** expresa de forma directa la acción del tablero y es fácil de leer para el alumno.
- **Consecuencias / a revisar más adelante:** se aparta del estilo REST orientado a recursos; en s09 (contrato v1) revisamos si conviene migrar a PATCH.
