"""Repositorio de etiquetas sobre PostgreSQL (s10).

Lectura de etiquetas (apoyo para clasificar tareas): listar todas y validar que un
conjunto de ids exista. Mapea ORM <-> dominio.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import EtiquetaORM
from app.models.etiqueta import Etiqueta


def _a_dominio(fila: EtiquetaORM) -> Etiqueta:
    return Etiqueta(
        id=fila.id,
        nombre=fila.nombre,
        color=fila.color,
        created_at=fila.created_at,
        updated_at=fila.updated_at,
    )


class RepositorioEtiquetasSQL:
    def __init__(self, session: Session) -> None:
        self._session = session

    def listar(self) -> list[Etiqueta]:
        filas = self._session.scalars(select(EtiquetaORM).order_by(EtiquetaORM.id)).all()
        return [_a_dominio(f) for f in filas]

    def ids_inexistentes(self, etiqueta_ids: list[int]) -> list[int]:
        """Devuelve los ids que NO existen (vacío si están todos)."""
        if not etiqueta_ids:
            return []
        existentes = set(
            self._session.scalars(
                select(EtiquetaORM.id).where(EtiquetaORM.id.in_(etiqueta_ids))
            ).all()
        )
        return [i for i in etiqueta_ids if i not in existentes]
