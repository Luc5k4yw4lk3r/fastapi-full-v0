"""Punto de entrada de la aplicación TaskFlow (s10).

Monta la API v1 (contrato de s09) y el endpoint de lectura para agentes (s08). Al iniciar
(`lifespan`) crea el esquema en PostgreSQL (create_all) y siembra equipo/proyecto por
defecto. Registra exception handlers que traducen las excepciones de dominio a códigos
HTTP, para que los routers queden finos. Este tag cierra el backend.

Ejecutar con: `uvicorn app.main:app --env-file .env`.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select

from app.db.database import Base, SessionLocal, engine
from app.db.models import EquipoORM, ProyectoORM  # noqa: F401 (registra las tablas)
from app.routers import agentes
from app.routers import v1 as api_v1
from app.services.errores import (
    EquipoNoEncontrado,
    EtiquetaNoEncontrada,
    ProyectoNoEncontrado,
    TareaNoEncontrada,
    UsuarioNoEncontrado,
)


def _crear_esquema_y_seed() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
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


app = FastAPI(title="TaskFlow", version="1.0.0", lifespan=lifespan)

app.include_router(api_v1.router)
app.include_router(agentes.router)


# --- Traducción de excepciones de dominio a HTTP 404 ---
def _registrar_handler(excepcion: type[Exception], plantilla) -> None:
    async def handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": plantilla(exc)})

    app.add_exception_handler(excepcion, handler)


_registrar_handler(EquipoNoEncontrado, lambda e: f"El equipo {e.args[0]} no existe")
_registrar_handler(ProyectoNoEncontrado, lambda e: f"El proyecto {e.args[0]} no existe")
_registrar_handler(TareaNoEncontrada, lambda e: f"La tarea {e.args[0]} no existe")
_registrar_handler(UsuarioNoEncontrado, lambda e: f"El usuario {e.args[0]} no existe")
_registrar_handler(EtiquetaNoEncontrada, lambda e: f"Etiquetas inexistentes: {e.args[0]}")


@app.get("/health", tags=["infra"])
def health() -> dict[str, str]:
    """Chequeo simple para verificar que el servidor responde."""
    return {"status": "ok"}
