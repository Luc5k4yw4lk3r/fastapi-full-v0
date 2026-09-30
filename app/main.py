"""Punto de entrada de la aplicación TaskFlow (s07).

Crea la instancia de FastAPI que levanta Uvicorn y monta el router de tareas. Al iniciar
(`lifespan`) crea el esquema en PostgreSQL (create_all, idempotente) y siembra un equipo y
un proyecto por defecto para que el flujo de crear tareas funcione. Es la "cima" de la
arquitectura en capas: acá se ensambla todo, sin lógica de negocio.

Ejecutar con: `uvicorn app.main:app --env-file .env` (para cargar DATABASE_URL).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.database import Base, SessionLocal, engine
from app.db.models import EquipoORM, ProyectoORM  # noqa: F401 (registra las tablas)
from app.routers import tareas


def _crear_esquema_y_seed() -> None:
    # create_all es idempotente: crea las tablas que falten a partir de los modelos ORM.
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        # Seed mínimo: equipo y proyecto por defecto (id=1) para las tareas nuevas.
        if db.get(EquipoORM, 1) is None:
            db.add(EquipoORM(id=1, nombre="Core"))
        if db.get(ProyectoORM, 1) is None:
            db.add(ProyectoORM(id=1, nombre="General", equipo_id=1))
        db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _crear_esquema_y_seed()
    yield


app = FastAPI(title="TaskFlow", version="0.7.0", lifespan=lifespan)

app.include_router(tareas.router)


@app.get("/health", tags=["infra"])
def health() -> dict[str, str]:
    """Chequeo simple para verificar que el servidor responde."""
    return {"status": "ok"}
