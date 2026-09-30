"""Repositorio de proyectos sobre PostgreSQL (s07).

Reemplaza al repositorio en memoria de s05 con la misma interfaz (obtener / existe).
Trabaja sobre una Session de SQLAlchemy y mapea la fila ORM al dominio. Ya no siembra
datos: el seed del proyecto por defecto se hace al iniciar la app (app/main.py).
"""

from sqlalchemy.orm import Session

from app.db.models import ProyectoORM
from app.models.proyecto import Proyecto


def _a_dominio(fila: ProyectoORM) -> Proyecto:
    return Proyecto(
        id=fila.id,
        nombre=fila.nombre,
        equipo_id=fila.equipo_id,
        descripcion=fila.descripcion,
        created_at=fila.created_at,
        updated_at=fila.updated_at,
    )


class RepositorioProyectosSQL:
    def __init__(self, session: Session) -> None:
        self._session = session

    def obtener(self, proyecto_id: int) -> Proyecto | None:
        fila = self._session.get(ProyectoORM, proyecto_id)
        return _a_dominio(fila) if fila is not None else None

    def existe(self, proyecto_id: int) -> bool:
        return self._session.get(ProyectoORM, proyecto_id) is not None
