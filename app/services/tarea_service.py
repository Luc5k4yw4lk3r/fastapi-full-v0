"""Capa service: casos de uso de tareas (crear, listar, mover).

Orquesta la lógica de negocio apoyándose en los repositorios, sin conocer HTTP ni el
detalle de almacenamiento. Levanta excepciones de dominio propias (ProyectoNoEncontrado,
TareaNoEncontrada) que el router traduce a códigos HTTP. Así la regla de negocio no
depende de FastAPI y podría reutilizarse desde otro punto de entrada.
"""

from app.models.estado import Estado
from app.models.tarea import Tarea
from app.repositories.proyecto_repository import RepositorioProyectosEnMemoria
from app.repositories.tarea_repository import RepositorioTareasEnMemoria


class ProyectoNoEncontrado(Exception):
    """El proyecto referenciado por la tarea no existe."""


class TareaNoEncontrada(Exception):
    """No hay ninguna tarea con ese id."""


class ServicioTareas:
    def __init__(
        self,
        repo_tareas: RepositorioTareasEnMemoria,
        repo_proyectos: RepositorioProyectosEnMemoria,
    ) -> None:
        self._repo_tareas = repo_tareas
        self._repo_proyectos = repo_proyectos

    def crear_tarea(self, tarea: Tarea) -> Tarea:
        # Regla de negocio: una tarea siempre pertenece a un proyecto existente.
        if not self._repo_proyectos.existe(tarea.proyecto_id):
            raise ProyectoNoEncontrado(tarea.proyecto_id)
        # El estado inicial siempre es BACKLOG, sin importar lo que mande el cliente.
        tarea.id = None
        tarea.estado = Estado.BACKLOG
        return self._repo_tareas.crear(tarea)

    def listar_tareas(self) -> list[Tarea]:
        return self._repo_tareas.listar()

    def mover_tarea(self, tarea_id: int, nuevo_estado: Estado) -> Tarea:
        tarea = self._repo_tareas.obtener(tarea_id)
        if tarea is None:
            raise TareaNoEncontrada(tarea_id)
        tarea.estado = nuevo_estado
        return self._repo_tareas.guardar(tarea)
