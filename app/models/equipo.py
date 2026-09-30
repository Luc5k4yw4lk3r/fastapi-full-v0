"""Entidad de dominio Equipo (s06).

Agrupa usuarios y es dueño de proyectos. La relación con Usuario es M:N y se modela del
lado de Usuario (`equipo_ids`) para no duplicar la lista de membresías en ambos lados;
la relación con Proyecto es 1:N (un equipo tiene varios proyectos). Sin persistencia.
"""

from app.models.base import EntidadConTiempos


class Equipo(EntidadConTiempos):
    id: int
    nombre: str
