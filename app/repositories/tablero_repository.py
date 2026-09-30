"""Repositorio de lectura del tablero para agentes (s08).

Consulta un proyecto y sus tareas en PostgreSQL con carga anticipada de relaciones
(responsable, etiquetas, comentarios+autor, equipo) y arma el DTO autocontenido
`TableroAgente`. Concentra acá las queries y el mapeo ORM -> vista, para no filtrar el
ORM hacia el service ni el router. Es solo lectura: no modifica nada.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import ComentarioORM, ProyectoORM, TareaORM
from app.models.estado import Estado
from app.models.tablero import (
    ColumnasTablero,
    ComentarioVista,
    EquipoVista,
    EtiquetaVista,
    ProyectoVista,
    ResumenTablero,
    TableroAgente,
    TareaVista,
)


def _a_tarea_vista(t: TareaORM) -> TareaVista:
    return TareaVista(
        id=t.id,
        titulo=t.titulo,
        descripcion=t.descripcion,
        responsable=t.responsable.nombre if t.responsable else None,
        etiquetas=[EtiquetaVista(nombre=e.nombre, color=e.color) for e in t.etiquetas],
        comentarios=[
            ComentarioVista(autor=c.autor.nombre, texto=c.texto, fecha=c.created_at)
            for c in t.comentarios
        ],
    )


class RepositorioTableroSQL:
    def __init__(self, session: Session) -> None:
        self._session = session

    def obtener_tablero(self, proyecto_id: int) -> TableroAgente | None:
        proyecto = self._session.scalars(
            select(ProyectoORM)
            .where(ProyectoORM.id == proyecto_id)
            .options(selectinload(ProyectoORM.equipo))
        ).first()
        if proyecto is None:
            return None

        tareas = self._session.scalars(
            select(TareaORM)
            .where(TareaORM.proyecto_id == proyecto_id)
            .order_by(TareaORM.id)
            .options(
                selectinload(TareaORM.responsable),
                selectinload(TareaORM.etiquetas),
                selectinload(TareaORM.comentarios).selectinload(ComentarioORM.autor),
            )
        ).all()

        columnas = ColumnasTablero()
        destino = {
            Estado.BACKLOG.value: columnas.backlog,
            Estado.EN_PROGRESO.value: columnas.en_progreso,
            Estado.HECHO.value: columnas.hecho,
        }
        for t in tareas:
            destino[t.estado].append(_a_tarea_vista(t))

        resumen = ResumenTablero(
            total_tareas=len(tareas),
            por_estado={
                "backlog": len(columnas.backlog),
                "en_progreso": len(columnas.en_progreso),
                "hecho": len(columnas.hecho),
            },
        )
        return TableroAgente(
            generado_en=datetime.now(timezone.utc),
            proyecto=ProyectoVista(
                id=proyecto.id,
                nombre=proyecto.nombre,
                descripcion=proyecto.descripcion,
                equipo=EquipoVista(nombre=proyecto.equipo.nombre),
            ),
            resumen=resumen,
            columnas=columnas,
        )
