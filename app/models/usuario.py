"""Entidad de dominio Usuario (s06).

Persona que usa TaskFlow: crea proyectos/tareas, comenta y puede ser responsable de una
tarea. Un usuario puede pertenecer a varios equipos (relación M:N), representada acá por
la lista `equipo_ids` (en s07 esto se vuelve una tabla de membresías). Sin persistencia.
"""

from app.models.base import EntidadConTiempos


class Usuario(EntidadConTiempos):
    id: int
    nombre: str
    email: str
    equipo_ids: list[int] = []  # M:N con Equipo (membresías)
