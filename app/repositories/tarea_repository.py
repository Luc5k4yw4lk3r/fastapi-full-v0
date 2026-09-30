"""Repositorio de tareas sobre PostgreSQL (s10).

Implementa el acceso a datos de tareas para la API v1: crear, obtener, listar con
filtros/orden/paginación, actualizar, mover (guardar) y eliminar. Mantiene el mapeo
ORM <-> dominio acá, así el dominio no importa SQLAlchemy. No hace commit: la transacción
la controla el service.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.models import EtiquetaORM, TareaORM
from app.models.tarea import Tarea

# Campos permitidos para ordenar (evita inyección por el query param `orden`).
_ORDENABLES = {"id", "titulo", "estado", "created_at", "updated_at"}


def _a_dominio(fila: TareaORM) -> Tarea:
    return Tarea(
        id=fila.id,
        titulo=fila.titulo,
        descripcion=fila.descripcion,
        estado=fila.estado,
        proyecto_id=fila.proyecto_id,
        responsable_id=fila.responsable_id,
        etiqueta_ids=sorted(e.id for e in fila.etiquetas),
        created_at=fila.created_at,
        updated_at=fila.updated_at,
    )


class RepositorioTareasSQL:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _etiquetas_orm(self, etiqueta_ids: list[int]) -> list[EtiquetaORM]:
        if not etiqueta_ids:
            return []
        return list(
            self._session.scalars(
                select(EtiquetaORM).where(EtiquetaORM.id.in_(etiqueta_ids))
            ).all()
        )

    def crear(self, tarea: Tarea) -> Tarea:
        fila = TareaORM(
            titulo=tarea.titulo,
            descripcion=tarea.descripcion,
            estado=tarea.estado.value,
            proyecto_id=tarea.proyecto_id,
            responsable_id=tarea.responsable_id,
            etiquetas=self._etiquetas_orm(tarea.etiqueta_ids),
        )
        self._session.add(fila)
        self._session.flush()
        return _a_dominio(fila)

    def obtener(self, tarea_id: int) -> Tarea | None:
        fila = self._session.get(TareaORM, tarea_id)
        return _a_dominio(fila) if fila is not None else None

    def listar(
        self,
        *,
        proyecto_id: int | None = None,
        estado: str | None = None,
        responsable_id: int | None = None,
        etiqueta: str | None = None,
        orden: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Tarea], int]:
        consulta = select(TareaORM)
        if proyecto_id is not None:
            consulta = consulta.where(TareaORM.proyecto_id == proyecto_id)
        if estado is not None:
            consulta = consulta.where(TareaORM.estado == estado)
        if responsable_id is not None:
            consulta = consulta.where(TareaORM.responsable_id == responsable_id)
        if etiqueta is not None:
            consulta = consulta.where(TareaORM.etiquetas.any(EtiquetaORM.nombre == etiqueta))

        # total (sin paginar) sobre la misma condición
        total = self._session.scalar(
            select(func.count()).select_from(consulta.subquery())
        )

        consulta = consulta.order_by(_clausula_orden(orden)).limit(limit).offset(offset)
        consulta = consulta.options(selectinload(TareaORM.etiquetas))
        filas = self._session.scalars(consulta).all()
        return [_a_dominio(f) for f in filas], int(total or 0)

    def guardar(self, tarea: Tarea) -> Tarea:
        """Actualiza una tarea existente (campos escalares + etiquetas)."""
        fila = self._session.get(TareaORM, tarea.id)
        fila.titulo = tarea.titulo
        fila.descripcion = tarea.descripcion
        fila.estado = tarea.estado.value
        fila.proyecto_id = tarea.proyecto_id
        fila.responsable_id = tarea.responsable_id
        fila.etiquetas = self._etiquetas_orm(tarea.etiqueta_ids)
        self._session.flush()
        return _a_dominio(fila)

    def eliminar(self, tarea_id: int) -> bool:
        fila = self._session.get(TareaORM, tarea_id)
        if fila is None:
            return False
        self._session.delete(fila)
        self._session.flush()
        return True


def _clausula_orden(orden: str | None):
    """Traduce el query param `orden` (ej. '-created_at') a una cláusula ORDER BY."""
    if not orden:
        return TareaORM.id.asc()
    descendente = orden.startswith("-")
    campo = orden[1:] if descendente else orden
    if campo not in _ORDENABLES:
        campo = "id"
    columna = getattr(TareaORM, campo)
    return columna.desc() if descendente else columna.asc()
