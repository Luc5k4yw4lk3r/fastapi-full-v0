"""Repositorio de comentarios sobre PostgreSQL (s10).

Crear y listar (paginado) comentarios de una tarea, con mapeo ORM <-> dominio. No hace
commit: la transacción la controla el service.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import ComentarioORM
from app.models.comentario import Comentario


def _a_dominio(fila: ComentarioORM) -> Comentario:
    return Comentario(
        id=fila.id,
        tarea_id=fila.tarea_id,
        autor_id=fila.autor_id,
        texto=fila.texto,
        created_at=fila.created_at,
        updated_at=fila.updated_at,
    )


class RepositorioComentariosSQL:
    def __init__(self, session: Session) -> None:
        self._session = session

    def crear(self, comentario: Comentario) -> Comentario:
        fila = ComentarioORM(
            tarea_id=comentario.tarea_id,
            autor_id=comentario.autor_id,
            texto=comentario.texto,
        )
        self._session.add(fila)
        self._session.flush()
        return _a_dominio(fila)

    def listar_por_tarea(
        self, tarea_id: int, *, limit: int = 20, offset: int = 0
    ) -> tuple[list[Comentario], int]:
        base = select(ComentarioORM).where(ComentarioORM.tarea_id == tarea_id)
        total = self._session.scalar(select(func.count()).select_from(base.subquery()))
        filas = self._session.scalars(
            base.order_by(ComentarioORM.id.asc()).limit(limit).offset(offset)
        ).all()
        return [_a_dominio(f) for f in filas], int(total or 0)
