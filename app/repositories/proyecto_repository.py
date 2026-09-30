"""Repositorio de proyectos en memoria (s05).

Guarda los proyectos en un dict indexado por id. Para el prototipo viene sembrado
con un proyecto por defecto ("General"), así las tareas pueden referenciar un proyecto
existente sin necesitar todavía endpoints de proyectos. En s07 esta clase se reemplaza
por una implementación sobre PostgreSQL manteniendo la misma interfaz.
"""

from app.models.proyecto import Proyecto


class RepositorioProyectosEnMemoria:
    def __init__(self) -> None:
        # Sembramos un proyecto por defecto para que las tareas tengan dónde vivir.
        # equipo_id=1 es conceptual por ahora; el cableado real de equipos llega en s07.
        self._proyectos: dict[int, Proyecto] = {
            1: Proyecto(id=1, nombre="General", equipo_id=1),
        }

    def obtener(self, proyecto_id: int) -> Proyecto | None:
        return self._proyectos.get(proyecto_id)

    def existe(self, proyecto_id: int) -> bool:
        return proyecto_id in self._proyectos
