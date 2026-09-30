"""Capa service: casos de uso de tareas (crear, listar, mover).

Orquesta la lógica de negocio apoyándose en los repositorios, sin conocer HTTP ni el
detalle de almacenamiento. En s07 además actúa como **unit of work**: es el dueño de la
transacción, así que confirma con `commit` las operaciones de escritura y hace `rollback`
si algo falla (garantizando atomicidad al mover una tarea). Sigue levantando excepciones
de dominio propias que el router traduce a códigos HTTP.
"""

from sqlalchemy.orm import Session

from app.models.estado import Estado
from app.models.tarea import Tarea
from app.repositories.proyecto_repository import RepositorioProyectosSQL
from app.repositories.tarea_repository import RepositorioTareasSQL


class ProyectoNoEncontrado(Exception):
    """El proyecto referenciado por la tarea no existe."""


class TareaNoEncontrada(Exception):
    """No hay ninguna tarea con ese id."""


class ServicioTareas:
    def __init__(
        self,
        repo_tareas: RepositorioTareasSQL,
        repo_proyectos: RepositorioProyectosSQL,
        session: Session,
    ) -> None:
        self._repo_tareas = repo_tareas
        self._repo_proyectos = repo_proyectos
        self._session = session

    def crear_tarea(self, tarea: Tarea) -> Tarea:
        # Regla de negocio: una tarea siempre pertenece a un proyecto existente.
        if not self._repo_proyectos.existe(tarea.proyecto_id):
            raise ProyectoNoEncontrado(tarea.proyecto_id)
        # El estado inicial siempre es BACKLOG, sin importar lo que mande el cliente.
        tarea.id = None
        tarea.estado = Estado.BACKLOG
        try:
            creada = self._repo_tareas.crear(tarea)
            self._session.commit()
            return creada
        except Exception:
            self._session.rollback()
            raise

    def listar_tareas(self) -> list[Tarea]:
        return self._repo_tareas.listar()

    def mover_tarea(self, tarea_id: int, nuevo_estado: Estado) -> Tarea:
        tarea = self._repo_tareas.obtener(tarea_id)
        if tarea is None:
            raise TareaNoEncontrada(tarea_id)
        tarea.estado = nuevo_estado
        try:
            actualizada = self._repo_tareas.guardar(tarea)
            self._session.commit()  # transacción: la tarea queda movida atómicamente
            return actualizada
        except Exception:
            self._session.rollback()
            raise
