"""Capa service: casos de uso de tareas para la API v1 (s10).

CRUD de tareas + mover estado, apoyándose en los repositorios y validando reglas de
negocio (el proyecto/responsable/etiquetas referenciados deben existir). Actúa como
unit of work: confirma con commit las escrituras y hace rollback ante error. No conoce
HTTP; levanta excepciones de dominio (app/services/errores.py) que el router traduce.
"""

from sqlalchemy.orm import Session

from app.models.estado import Estado
from app.models.tarea import Tarea
from app.repositories.etiqueta_repository import RepositorioEtiquetasSQL
from app.repositories.proyecto_repository import RepositorioProyectosSQL
from app.repositories.tarea_repository import RepositorioTareasSQL
from app.repositories.usuario_repository import RepositorioUsuariosSQL
from app.services.errores import (
    EtiquetaNoEncontrada,
    ProyectoNoEncontrado,
    TareaNoEncontrada,
    UsuarioNoEncontrado,
)


class ServicioTareas:
    def __init__(
        self,
        repo_tareas: RepositorioTareasSQL,
        repo_proyectos: RepositorioProyectosSQL,
        repo_usuarios: RepositorioUsuariosSQL,
        repo_etiquetas: RepositorioEtiquetasSQL,
        session: Session,
    ) -> None:
        self._repo_tareas = repo_tareas
        self._repo_proyectos = repo_proyectos
        self._repo_usuarios = repo_usuarios
        self._repo_etiquetas = repo_etiquetas
        self._session = session

    def _validar_referencias(
        self, proyecto_id: int | None, responsable_id: int | None, etiqueta_ids: list[int]
    ) -> None:
        if proyecto_id is not None and not self._repo_proyectos.existe(proyecto_id):
            raise ProyectoNoEncontrado(proyecto_id)
        if responsable_id is not None and not self._repo_usuarios.existe(responsable_id):
            raise UsuarioNoEncontrado(responsable_id)
        faltantes = self._repo_etiquetas.ids_inexistentes(etiqueta_ids)
        if faltantes:
            raise EtiquetaNoEncontrada(faltantes)

    # --- comandos (escritura) ---
    def crear_tarea(self, tarea: Tarea) -> Tarea:
        self._validar_referencias(tarea.proyecto_id, tarea.responsable_id, tarea.etiqueta_ids)
        # El id lo asigna el repositorio y el estado inicial siempre es BACKLOG.
        tarea.id = None
        tarea.estado = Estado.BACKLOG
        try:
            creada = self._repo_tareas.crear(tarea)
            self._session.commit()
            return creada
        except Exception:
            self._session.rollback()
            raise

    def actualizar_tarea(self, tarea_id: int, cambios: dict) -> Tarea:
        tarea = self._repo_tareas.obtener(tarea_id)
        if tarea is None:
            raise TareaNoEncontrada(tarea_id)
        # Solo se aplican los campos presentes en el pedido (PATCH parcial).
        if "titulo" in cambios:
            tarea.titulo = cambios["titulo"]
        if "descripcion" in cambios:
            tarea.descripcion = cambios["descripcion"]
        if "responsable_id" in cambios:
            tarea.responsable_id = cambios["responsable_id"]
        if "etiqueta_ids" in cambios:
            tarea.etiqueta_ids = cambios["etiqueta_ids"] or []
        self._validar_referencias(None, tarea.responsable_id, tarea.etiqueta_ids)
        try:
            actualizada = self._repo_tareas.guardar(tarea)
            self._session.commit()
            return actualizada
        except Exception:
            self._session.rollback()
            raise

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

    def eliminar_tarea(self, tarea_id: int) -> None:
        if not self._repo_tareas.eliminar(tarea_id):
            raise TareaNoEncontrada(tarea_id)
        self._session.commit()

    # --- consultas (lectura) ---
    def obtener_tarea(self, tarea_id: int) -> Tarea:
        tarea = self._repo_tareas.obtener(tarea_id)
        if tarea is None:
            raise TareaNoEncontrada(tarea_id)
        return tarea

    def listar_tareas(self, **filtros) -> tuple[list[Tarea], int]:
        return self._repo_tareas.listar(**filtros)
