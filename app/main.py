"""Punto de entrada de la aplicación TaskFlow (s08).

Crea la instancia de FastAPI que levanta Uvicorn y monta los routers (tareas + lectura
para agentes). Al iniciar (`lifespan`) crea el esquema en PostgreSQL (create_all,
idempotente) y siembra —por nombre, sin ids fijos— un equipo y un proyecto por defecto
para que el flujo de crear tareas funcione. Los datos realistas se cargan aparte con
`scripts/seed.py`. Es la "cima" de la arquitectura en capas: acá se ensambla todo.

Ejecutar con: `uvicorn app.main:app --env-file .env` (para cargar DATABASE_URL).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select

from app.db.database import Base, SessionLocal, engine
from app.db.models import EquipoORM, ProyectoORM  # noqa: F401 (registra las tablas)
from app.routers import agentes, tareas


def _crear_esquema_y_seed() -> None:
    # create_all es idempotente: crea las tablas que falten a partir de los modelos ORM.
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        # Seed mínimo por nombre (sin id fijo, para que la secuencia avance bien).
        equipo = db.scalars(select(EquipoORM).where(EquipoORM.nombre == "Core")).first()
        if equipo is None:
            equipo = EquipoORM(nombre="Core")
            db.add(equipo)
            db.flush()
        if db.scalars(select(ProyectoORM).where(ProyectoORM.nombre == "General")).first() is None:
            db.add(ProyectoORM(nombre="General", equipo_id=equipo.id))
        db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _crear_esquema_y_seed()
    yield


app = FastAPI(title="TaskFlow", version="0.8.0", lifespan=lifespan)

app.include_router(tareas.router)
app.include_router(agentes.router)


@app.get("/health", tags=["infra"])
def health() -> dict[str, str]:
    """Chequeo simple para verificar que el servidor responde."""
    return {"status": "ok"}
