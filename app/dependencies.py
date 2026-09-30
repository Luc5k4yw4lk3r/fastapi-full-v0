"""Composición de dependencias de la app (s05).

Crea una única instancia de cada repositorio (en memoria, viven mientras corre el
proceso) y del service, y las expone vía `Depends` de FastAPI. Centralizar el cableado
acá permite que en s07 cambiemos los repositorios por los de PostgreSQL tocando solo
este archivo, sin modificar routers ni services.
"""

from app.repositories.proyecto_repository import RepositorioProyectosEnMemoria
from app.repositories.tarea_repository import RepositorioTareasEnMemoria
from app.services.tarea_service import ServicioTareas

_repo_proyectos = RepositorioProyectosEnMemoria()
_repo_tareas = RepositorioTareasEnMemoria()
_servicio_tareas = ServicioTareas(_repo_tareas, _repo_proyectos)


def obtener_servicio_tareas() -> ServicioTareas:
    return _servicio_tareas
