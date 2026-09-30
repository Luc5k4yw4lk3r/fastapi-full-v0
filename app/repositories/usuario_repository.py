"""Repositorio de usuarios sobre PostgreSQL (s10).

Lectura de usuarios (apoyo para asignar responsables): listar (paginado), obtener y
comprobar existencia. Mapea ORM <-> dominio, incluyendo las membresías M:N como equipo_ids.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.models import UsuarioORM
from app.models.usuario import Usuario


def _a_dominio(fila: UsuarioORM) -> Usuario:
    return Usuario(
        id=fila.id,
        nombre=fila.nombre,
        email=fila.email,
        equipo_ids=sorted(e.id for e in fila.equipos),
        created_at=fila.created_at,
        updated_at=fila.updated_at,
    )


class RepositorioUsuariosSQL:
    def __init__(self, session: Session) -> None:
        self._session = session

    def obtener(self, usuario_id: int) -> Usuario | None:
        fila = self._session.get(UsuarioORM, usuario_id)
        return _a_dominio(fila) if fila is not None else None

    def existe(self, usuario_id: int) -> bool:
        return self._session.get(UsuarioORM, usuario_id) is not None

    def listar(self, *, limit: int = 20, offset: int = 0) -> tuple[list[Usuario], int]:
        total = self._session.scalar(select(func.count()).select_from(UsuarioORM))
        filas = self._session.scalars(
            select(UsuarioORM)
            .order_by(UsuarioORM.id.asc())
            .limit(limit)
            .offset(offset)
            .options(selectinload(UsuarioORM.equipos))
        ).all()
        return [_a_dominio(f) for f in filas], int(total or 0)
