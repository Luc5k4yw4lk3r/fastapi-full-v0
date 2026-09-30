"""Capa service: lectura de etiquetas para la API v1 (s10).

Apoyo para clasificar tareas: listar las etiquetas disponibles. Solo lectura.
"""

from app.models.etiqueta import Etiqueta
from app.repositories.etiqueta_repository import RepositorioEtiquetasSQL


class ServicioEtiquetas:
    def __init__(self, repo_etiquetas: RepositorioEtiquetasSQL) -> None:
        self._repo = repo_etiquetas

    def listar_etiquetas(self) -> list[Etiqueta]:
        return self._repo.listar()
