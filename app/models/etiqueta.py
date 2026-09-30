"""Entidad de dominio Etiqueta (s06).

Marca reutilizable que clasifica tareas (p. ej. "bug", "urgente"). Una etiqueta puede
estar en muchas tareas y una tarea puede tener muchas etiquetas (M:N); esa relación se
modela del lado de Tarea (`etiqueta_ids`). `color` es opcional. Sin persistencia.
"""

from app.models.base import EntidadConTiempos


class Etiqueta(EntidadConTiempos):
    id: int
    nombre: str
    color: str | None = None
