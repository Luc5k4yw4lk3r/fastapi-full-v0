"""Proveedores de services para la API v1 (s10).

Arman cada service por request sobre la Session de `get_db`, inyectando los repositorios
SQL que necesita. Centralizar el cableado acá mantiene los routers finos.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.comentario_repository import RepositorioComentariosSQL
from app.repositories.etiqueta_repository import RepositorioEtiquetasSQL
from app.repositories.proyecto_repository import RepositorioProyectosSQL
from app.repositories.tarea_repository import RepositorioTareasSQL
from app.repositories.usuario_repository import RepositorioUsuariosSQL
from app.services.comentario_service import ServicioComentarios
from app.services.etiqueta_service import ServicioEtiquetas
from app.services.proyecto_service import ServicioProyectos
from app.services.tarea_service import ServicioTareas
from app.services.usuario_service import ServicioUsuarios


def servicio_tareas(db: Session = Depends(get_db)) -> ServicioTareas:
    return ServicioTareas(
        RepositorioTareasSQL(db),
        RepositorioProyectosSQL(db),
        RepositorioUsuariosSQL(db),
        RepositorioEtiquetasSQL(db),
        db,
    )


def servicio_proyectos(db: Session = Depends(get_db)) -> ServicioProyectos:
    return ServicioProyectos(RepositorioProyectosSQL(db), db)


def servicio_comentarios(db: Session = Depends(get_db)) -> ServicioComentarios:
    return ServicioComentarios(
        RepositorioComentariosSQL(db),
        RepositorioTareasSQL(db),
        RepositorioUsuariosSQL(db),
        db,
    )


def servicio_usuarios(db: Session = Depends(get_db)) -> ServicioUsuarios:
    return ServicioUsuarios(RepositorioUsuariosSQL(db))


def servicio_etiquetas(db: Session = Depends(get_db)) -> ServicioEtiquetas:
    return ServicioEtiquetas(RepositorioEtiquetasSQL(db))
