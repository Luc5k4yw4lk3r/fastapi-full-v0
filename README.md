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

# 3. Servidor de la API (--env-file carga DATABASE_URL; al iniciar crea el esquema y el seed)
uvicorn app.main:app --reload --env-file .env
#   -> Swagger en http://127.0.0.1:8000/docs

# 4. Cliente de prueba (en otra terminal, con el server arriba)
python scripts/client.py
```

## Estado

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
