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

## [s06] ADR-001 — Tipo de base de datos para TaskFlow

- **Fecha:** 2026-09-30
- **Estado:** Aceptada

### Contexto: patrones de acceso de TaskFlow
- **Lecturas intensivas del tablero:** la operación más frecuente es traer todas las
  tareas de un proyecto, agrupadas/filtradas por estado, responsable y etiquetas. Requiere
  filtros y ordenamientos sobre relaciones (tarea → proyecto → equipo).
- **Escrituras concurrentes sobre tareas:** varios miembros mueven de estado, comentan y
  asignan tareas al mismo tiempo. Importa la consistencia (no perder una transición) y
  operaciones atómicas (mover + registrar actividad, comentar).
- **Datos fuertemente relacionados:** Usuario, Equipo, Proyecto, Tarea, Comentario y
  Etiqueta se referencian entre sí, con relaciones 1:N y M:N. La integridad referencial
  (no dejar comentarios huérfanos, no asignar a un usuario inexistente) es central.
- **Volumen moderado, esquema estable:** el modelo es conocido y no cambia por registro.

### Decisión
- **Alternativas consideradas:**
  - **Relacional (PostgreSQL)** — modela naturalmente las relaciones (FK, tablas de
    enlace M:N), da integridad referencial, transacciones ACID para mover/comentar y un
    lenguaje de consulta (SQL/JOIN) ideal para las vistas del tablero.
  - **Documental (MongoDB)** — bueno para datos jerárquicos y poco relacionados; acá
    obligaría a duplicar usuarios/etiquetas en cada documento o a hacer "joins" a mano,
    complicando la consistencia y las queries del tablero.
  - **Key-value (Redis)** — acceso por clave ultrarrápido, pero no es fuente de verdad con
    relaciones ni consultas por atributos; encajaría como caché más adelante, no ahora.
- **Elección:** **Relacional — PostgreSQL.**
- **Por qué:** los patrones dominantes (relaciones fuertes + integridad + transacciones +
  consultas filtradas del tablero) son exactamente lo que un motor relacional resuelve
  mejor. Coincide además con la infraestructura ya levantada en s05.
- **Consecuencias / a revisar más adelante:** habrá que definir el esquema ER y las tablas
  de enlace M:N (usuario–equipo, tarea–etiqueta) en s07. Si aparecieran lecturas del
  tablero muy calientes, se podría sumar Redis como caché (no como fuente de verdad).

### [s06] Modelado del dominio: relaciones por id y cardinalidades
- **Fecha:** 2026-09-30
- **Decisión:** las entidades se referencian **por id** (estilo FK) y las relaciones
  muchos-a-muchos se modelan de forma **realista (M:N)**.
- **Alternativas consideradas:**
  - Relaciones por id vs objetos anidados — anidar es cómodo en memoria pero duplica
    datos y choca con el modelo relacional de s07.
  - M:N realista vs simplificar a 1:N — 1:N tendría menos enlaces pero no refleja que un
    usuario está en varios equipos ni que una tarea tiene varias etiquetas.
- **Elección:** por id + M:N (Usuario↔Equipo vía `equipo_ids`, Tarea↔Etiqueta vía
  `etiqueta_ids`); N:1 por id para Proyecto→Equipo, Tarea→Proyecto, Tarea→responsable,
  Comentario→Tarea y Comentario→autor. Se agregan `created_at`/`updated_at` a todas.
- **Por qué:** se mapea 1:1 al esquema relacional que viene en s07 (FKs y tablas de
  enlace), evita duplicación y ciclos, y refleja cómo funciona un tablero real.
- **Consecuencias / a revisar más adelante:** en s07, las listas de ids M:N se vuelven
  tablas de enlace; los timestamps (hoy en `None`) los poblará la capa de persistencia.

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
