"""Composición de dependencias de la app (s07).

Arma el service **por request** sobre la Session que entrega `get_db`: crea los
repositorios SQL bound a esa sesión y con ellos el ServicioTareas. Al vivir todo dentro
del ciclo de vida de la Session, cada request tiene su propia transacción. Cambiar de
almacenamiento (memoria -> Postgres) se resolvió tocando solo esta capa y los repos.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.proyecto_repository import RepositorioProyectosSQL
from app.repositories.tarea_repository import RepositorioTareasSQL
from app.services.tarea_service import ServicioTareas


def obtener_servicio_tareas(db: Session = Depends(get_db)) -> ServicioTareas:
    repo_tareas = RepositorioTareasSQL(db)
    repo_proyectos = RepositorioProyectosSQL(db)
    return ServicioTareas(repo_tareas, repo_proyectos, db)
