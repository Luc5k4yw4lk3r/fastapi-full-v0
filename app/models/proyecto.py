"""Entidad de dominio Proyecto (ampliada en s06).

Un proyecto pertenece a un equipo (relación N:1 por id, `equipo_id`) y agrupa tareas.
En s05 era solo id + nombre; en s06 se completa con el dueño (equipo), descripción y
timestamps. Sigue siendo una clase Pydantic sin persistencia (la conexión llega en s07).
"""

from app.models.base import EntidadConTiempos


class Proyecto(EntidadConTiempos):
    id: int
    nombre: str
    equipo_id: int
    descripcion: str | None = None
