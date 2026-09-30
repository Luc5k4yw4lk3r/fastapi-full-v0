"""Repositorio de proyectos sobre PostgreSQL (s10).

CRUD de proyectos para la API v1, con el mapeo ORM <-> dominio contenido acá. No hace
commit: la transacción la controla el service.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import EquipoORM, ProyectoORM
from app.models.proyecto import Proyecto

_ORDENABLES = {"id", "nombre", "created_at", "updated_at"}


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

    def crear(self, proyecto: Proyecto) -> Proyecto:
        fila = ProyectoORM(
            nombre=proyecto.nombre,
            equipo_id=proyecto.equipo_id,
            descripcion=proyecto.descripcion,
        )
        self._session.add(fila)
        self._session.flush()
        return _a_dominio(fila)

    def obtener(self, proyecto_id: int) -> Proyecto | None:
        fila = self._session.get(ProyectoORM, proyecto_id)
        return _a_dominio(fila) if fila is not None else None

    def existe(self, proyecto_id: int) -> bool:
        return self._session.get(ProyectoORM, proyecto_id) is not None

    def equipo_existe(self, equipo_id: int) -> bool:
        return self._session.get(EquipoORM, equipo_id) is not None

    def listar(
        self, *, orden: str | None = None, limit: int = 20, offset: int = 0
    ) -> tuple[list[Proyecto], int]:
        total = self._session.scalar(select(func.count()).select_from(ProyectoORM))
        consulta = (
            select(ProyectoORM)
            .order_by(_clausula_orden(orden))
            .limit(limit)
            .offset(offset)
        )
        filas = self._session.scalars(consulta).all()
        return [_a_dominio(f) for f in filas], int(total or 0)

    def guardar(self, proyecto: Proyecto) -> Proyecto:
        fila = self._session.get(ProyectoORM, proyecto.id)
        fila.nombre = proyecto.nombre
        fila.descripcion = proyecto.descripcion
        self._session.flush()
        return _a_dominio(fila)

    def eliminar(self, proyecto_id: int) -> bool:
        fila = self._session.get(ProyectoORM, proyecto_id)
        if fila is None:
            return False
        self._session.delete(fila)
        self._session.flush()
        return True


def _clausula_orden(orden: str | None):
    if not orden:
        return ProyectoORM.id.asc()
    descendente = orden.startswith("-")
    campo = orden[1:] if descendente else orden
    if campo not in _ORDENABLES:
        campo = "id"
    columna = getattr(ProyectoORM, campo)
    return columna.desc() if descendente else columna.asc()
