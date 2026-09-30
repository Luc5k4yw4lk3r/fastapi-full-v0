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

### [s08] Endpoint de lectura para agentes: forma autocontenida
- **Fecha:** 2026-09-30
- **Decisión:** un endpoint que devuelve el **tablero de un proyecto autocontenido**
  (`GET /agent/proyectos/{id}/tablero`): proyecto + equipo + tareas agrupadas por columna,
  con responsable, etiquetas y comentarios ya resueltos (nombres, no ids), más una marca de
  frescura `generado_en` y un resumen.
- **Alternativas consideradas:**
  - **Tablero de proyecto autocontenido** — el agente entiende todo el estado en una llamada.
  - **Contexto de una sola tarea** — más acotado; requiere varias llamadas para ver el tablero.
- **Elección:** tablero de proyecto autocontenido.
- **Por qué:** minimiza el ida y vuelta del agente y le da el contexto resuelto de una vez,
  que es justo lo que necesita para razonar sobre el estado.
- **Consecuencias / a revisar más adelante:** la respuesta es más pesada y denormalizada;
  para tableros muy grandes convendría paginar/filtrar (eso se formaliza en el contrato de s09/s10).

### [s08] Estrategia de seeds: idempotente por clave natural
- **Fecha:** 2026-09-30
- **Decisión:** `scripts/seed.py` **idempotente por clave natural** (nombre/email/título),
  sin ids fijos.
- **Alternativas consideradas:**
  - **Reset (truncate + insert)** — estado 100% reproducible, pero destruye datos existentes.
  - **Idempotente (insert si falta)** — conserva lo que haya y no duplica.
- **Elección:** idempotente.
- **Por qué:** se puede correr varias veces sin romper datos ni la app, y al no usar ids fijos
  las secuencias de Postgres avanzan bien (evita colisiones con las filas creadas por la API).
- **Consecuencias / a revisar más adelante:** el estado final depende de lo que ya existiera;
  si se quiere un dataset limpio y fijo, se puede truncar antes de sembrar.

### [s07] Stack de ORM y separación dominio/persistencia
- **Fecha:** 2026-09-30
- **Decisión:** SQLAlchemy 2.0 con modelos ORM **separados** de las entidades de dominio Pydantic; el repositorio mapea ORM ⇄ dominio. Driver psycopg3 síncrono.
- **Alternativas consideradas:**
  - **SQLAlchemy 2.0, ORM separado** — `TareaORM` (persistencia) distinta de `Tarea` (dominio); mapeo en el repository.
  - **SQLModel** — una sola clase por entidad que es Pydantic + tabla; menos código pero funde dominio y persistencia.
  - **SQL crudo (psycopg)** — control total, pero mucho boilerplate y mapeo manual para 6 entidades + M:N.
- **Elección:** SQLAlchemy 2.0 con ORM separado.
- **Por qué:** cumple la regla de capas de CLAUDE.md (el dominio en `app/models/` no importa SQLAlchemy), y deja el punto de mapeo explícito y testeable en la capa repository.
- **Consecuencias / a revisar más adelante:** hay que mantener el mapeo ORM⇄dominio (funciones `_a_dominio`); a cambio, cada capa evoluciona por separado.

### [s07] Gestión del esquema: create_all vs migraciones
- **Fecha:** 2026-09-30
- **Decisión:** crear el esquema con `Base.metadata.create_all()` al iniciar la app, más un seed mínimo (equipo/proyecto por defecto).
- **Alternativas consideradas:**
  - **create_all al iniciar** — simple y directo; crea lo que falte a partir de los modelos ORM.
  - **Alembic** — migraciones versionadas (upgrade/downgrade), estándar productivo pero con más maquinaria.
- **Elección:** create_all + seed.
- **Por qué:** para el alcance de s07 alcanza y evita introducir conceptos de migraciones todavía.
- **Consecuencias / a revisar más adelante:** `create_all` no versiona cambios de esquema ni altera tablas existentes; si el modelo evoluciona, Alembic entra más adelante.

### [s07] Capa de datos síncrona vs asíncrona
- **Fecha:** 2026-09-30
- **Decisión:** capa de datos **síncrona** (endpoints `def`, `Session` de SQLAlchemy, psycopg3 sync).
- **Alternativas consideradas:**
  - **Síncrona** — coherente con los endpoints `def` de s05/s06, más fácil de razonar y depurar.
  - **Asíncrona** — `async`/`AsyncSession`, mejor bajo alta concurrencia de I/O, pero propaga async por todas las capas.
- **Elección:** síncrona.
- **Por qué:** no hay necesidad real de async en el prototipo y mantiene el código simple; FastAPI corre los endpoints `def` en un threadpool.
- **Consecuencias / a revisar más adelante:** si en el futuro la concurrencia de I/O fuese un cuello de botella, se evaluaría migrar a async.

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
