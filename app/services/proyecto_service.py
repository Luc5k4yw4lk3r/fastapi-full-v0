"""Capa service: casos de uso de proyectos para la API v1 (s10).

CRUD de proyectos con validación (el equipo debe existir al crear) y control de la
transacción (commit/rollback). No conoce HTTP; levanta excepciones de dominio.
"""

from sqlalchemy.orm import Session

from app.models.proyecto import Proyecto
from app.repositories.proyecto_repository import RepositorioProyectosSQL
from app.services.errores import EquipoNoEncontrado, ProyectoNoEncontrado


class ServicioProyectos:
    def __init__(self, repo_proyectos: RepositorioProyectosSQL, session: Session) -> None:
        self._repo = repo_proyectos
        self._session = session

    def crear_proyecto(self, proyecto: Proyecto) -> Proyecto:
        if not self._repo.equipo_existe(proyecto.equipo_id):
            raise EquipoNoEncontrado(proyecto.equipo_id)
        proyecto.id = None
        try:
            creado = self._repo.crear(proyecto)
            self._session.commit()
            return creado
        except Exception:
            self._session.rollback()
            raise

    def obtener_proyecto(self, proyecto_id: int) -> Proyecto:
        proyecto = self._repo.obtener(proyecto_id)
        if proyecto is None:
            raise ProyectoNoEncontrado(proyecto_id)
        return proyecto

    def listar_proyectos(self, **filtros) -> tuple[list[Proyecto], int]:
        return self._repo.listar(**filtros)

    def actualizar_proyecto(self, proyecto_id: int, cambios: dict) -> Proyecto:
        proyecto = self._repo.obtener(proyecto_id)
        if proyecto is None:
            raise ProyectoNoEncontrado(proyecto_id)
        if "nombre" in cambios:
            proyecto.nombre = cambios["nombre"]
        if "descripcion" in cambios:
            proyecto.descripcion = cambios["descripcion"]
        try:
            actualizado = self._repo.guardar(proyecto)
            self._session.commit()
            return actualizado
        except Exception:
            self._session.rollback()
            raise

    def eliminar_proyecto(self, proyecto_id: int) -> None:
        if not self._repo.eliminar(proyecto_id):
            raise ProyectoNoEncontrado(proyecto_id)
        self._session.commit()
