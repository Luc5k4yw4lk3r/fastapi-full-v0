"""Repositorio de tareas sobre PostgreSQL (s07).

Reemplaza al repositorio en memoria de s05 manteniendo la MISMA interfaz
(crear / listar / obtener / guardar), por eso el service y el router casi no cambian.
Trabaja sobre una Session de SQLAlchemy y traduce entre la fila ORM (TareaORM) y la
entidad de dominio (Tarea, Pydantic): el mapeo vive acá, así el dominio no importa el ORM.
No hace commit: la transacción la controla el service (unit of work).
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import TareaORM
from app.models.tarea import Tarea


def _a_dominio(fila: TareaORM) -> Tarea:
    """Convierte una fila ORM en una entidad de dominio Pydantic."""
    return Tarea(
        id=fila.id,
        titulo=fila.titulo,
        descripcion=fila.descripcion,
        estado=fila.estado,
        proyecto_id=fila.proyecto_id,
        responsable_id=fila.responsable_id,
        etiqueta_ids=[e.id for e in fila.etiquetas],
        created_at=fila.created_at,
        updated_at=fila.updated_at,
    )


class RepositorioTareasSQL:
    def __init__(self, session: Session) -> None:
        self._session = session

    def crear(self, tarea: Tarea) -> Tarea:
        fila = TareaORM(
            titulo=tarea.titulo,
            descripcion=tarea.descripcion,
            estado=tarea.estado.value,
            proyecto_id=tarea.proyecto_id,
            responsable_id=tarea.responsable_id,
        )
        self._session.add(fila)
        self._session.flush()  # obtiene el id autogenerado sin cerrar la transacción
        return _a_dominio(fila)

    def listar(self) -> list[Tarea]:
        filas = self._session.scalars(select(TareaORM).order_by(TareaORM.id)).all()
        return [_a_dominio(f) for f in filas]

    def obtener(self, tarea_id: int) -> Tarea | None:
        fila = self._session.get(TareaORM, tarea_id)
        return _a_dominio(fila) if fila is not None else None

    def guardar(self, tarea: Tarea) -> Tarea:
        # Actualiza una tarea existente (p. ej. tras cambiarle el estado).
        fila = self._session.get(TareaORM, tarea.id)
        fila.titulo = tarea.titulo
        fila.descripcion = tarea.descripcion
        fila.estado = tarea.estado.value
        fila.proyecto_id = tarea.proyecto_id
        fila.responsable_id = tarea.responsable_id
        self._session.flush()
        return _a_dominio(fila)
