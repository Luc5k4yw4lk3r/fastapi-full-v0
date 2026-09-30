"""Capa service: caso de uso de lectura del tablero para agentes (s08).

Orquesta la obtención del tablero autocontenido delegando en el repositorio. Solo
lectura, sin transacciones de escritura. Levanta ProyectoNoEncontrado (reutilizada del
service de tareas) si el proyecto no existe, para que el router responda 404.
"""

from app.models.tablero import TableroAgente
from app.repositories.tablero_repository import RepositorioTableroSQL
from app.services.tarea_service import ProyectoNoEncontrado


class ServicioTablero:
    def __init__(self, repo_tablero: RepositorioTableroSQL) -> None:
        self._repo_tablero = repo_tablero

    def tablero_de_proyecto(self, proyecto_id: int) -> TableroAgente:
        tablero = self._repo_tablero.obtener_tablero(proyecto_id)
        if tablero is None:
            raise ProyectoNoEncontrado(proyecto_id)
        return tablero
