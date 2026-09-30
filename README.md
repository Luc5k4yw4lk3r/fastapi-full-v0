# TaskFlow

Aplicación de gestión de tareas para equipos (tipo mini-Trello), **sin ningún
componente de IA/LLM**. Es el proyecto que hilvana las sesiones **S05 a S12** del
Módulo 7 (Fundamentos de Software + System Design). Se construye de forma
**incremental**: una sesión = un incremento = un tag de git.

## Stack

- **Backend:** FastAPI (Python 3.12), organizado en capas.
- **Base de datos:** PostgreSQL en Docker (docker-compose). Es la única forma soportada
  de levantar la base.
- **Frontend:** HTML + JavaScript **vanilla** (desde s11). Sin frameworks ni build tools.

## Arquitectura en capas

```
router → service → repository → datos
(HTTP)   (dominio)  (persistencia)
```

El dominio nunca importa detalles de persistencia. El almacenamiento empieza en memoria
(s05) y pasa a PostgreSQL en s07, sin que cambie la interfaz de la capa `service`.

## Estructura del repo

```
app/          Backend en capas
  routers/    Endpoints HTTP (FastAPI)
  services/   Casos de uso / reglas de negocio
  repositories/ Acceso a datos (memoria -> PostgreSQL)
  models/     Entidades de dominio
frontend/     HTML + JS vanilla (desde s11)
docs/
  diagrams/   Diagramas en Mermaid
  trade-offs.md  Bitácora de decisiones de diseño
sessions/     Alcance de cada sesión (s05–s12)
```

## Cómo trabajamos

Cada sesión tiene su alcance en `sessions/sXX.md` (Objetivo / Entra / NO entra /
Entregables) y cierra con un tag `sXX`. Las reglas del proyecto y el protocolo de
sesión están en [`CLAUDE.md`](./CLAUDE.md).

- **s10** cierra el backend.
- **s12** es la versión entregable (TaskFlow full-stack).

## Cómo correr (s05)

```bash
# 1. Entorno e instalación
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Infraestructura de datos (Postgres en Docker)
cp .env.example .env          # si el puerto 5432 está ocupado, cambiá POSTGRES_PORT (y DATABASE_URL)
docker compose up -d

# 3. Datos de ejemplo realistas (idempotente; carga DATABASE_URL desde .env)
python scripts/seed.py

# 4. Servidor de la API (--env-file carga DATABASE_URL; al iniciar crea el esquema y el seed mínimo)
uvicorn app.main:app --reload --env-file .env
#   -> Swagger en http://127.0.0.1:8000/docs
#   -> Tablero para agentes: GET /agent/proyectos/1/tablero

# 5. Cliente de prueba (en otra terminal, con el server arriba)
python scripts/client.py
```

## Estado

**s09 — Contrato de la API (top-down).** Se diseñó el **contrato v1 antes de implementarlo**:
`docs/api-v1.yaml` (OpenAPI 3.1) con recursos en plural y en español, versionado `/v1`,
paginación/filtros/orden por query params y el cambio de estado como acción
`POST /v1/tareas/{id}/mover`. Se registró la **decisión de protocolo** (HTTP síncrono; cuándo
entrarían WebSockets o colas) en `docs/trade-offs.md`. La implementación es s10.

**s08 — Datos para agentes.** Se documentó la **frescura y el ciclo de vida** de los datos
(`docs/datos.md`), se agregó un script de **seeds realistas idempotente** (`scripts/seed.py`:
equipos, usuarios con membresías, proyectos, etiquetas, tareas y comentarios) y un **endpoint
de lectura para agentes** autocontenido: `GET /agent/proyectos/{id}/tablero` (proyecto + equipo
+ tareas por columna con responsable, etiquetas y comentarios resueltos, con marca de frescura).
Sin RAG ni vectores.

**s07 — PostgreSQL real.** La app se conecta a Postgres con **SQLAlchemy 2.0** (ORM en
`app/db/models.py`, separado del dominio Pydantic; el repository mapea ORM ⇄ dominio). El
**ER completo** (6 entidades + 2 tablas de enlace M:N) se crea al iniciar con `create_all`
+ un seed de equipo/proyecto por defecto. Los repositorios en memoria de s05 se migraron a
Postgres manteniendo la misma interfaz, y el service controla las **transacciones**
(commit/rollback). Los datos ahora **persisten** entre reinicios de la app.

**s06 — Decisión de almacenamiento + modelo de dominio.** Se eligió **PostgreSQL
(relacional)** con un ADR basado en los patrones de acceso (ver `docs/trade-offs.md`), y
se definió el **modelo de dominio completo** como clases Pydantic en `app/models/`:
Usuario, Equipo, Proyecto, Tarea, Comentario, Etiqueta (relaciones por id, M:N donde
corresponde, con timestamps). Todavía **sin persistencia real**: la conexión a Postgres
llega en s07.

**s05 — Prototipo mínimo.** API FastAPI en capas con Tarea/Proyecto en memoria (crear,
listar y mover tareas) + cliente httpx + PostgreSQL levantando en Docker (sin conectar).
Las dependencias se agregan en la sesión que las introduce (ver `requirements.txt`).
