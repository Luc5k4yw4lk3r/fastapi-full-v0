"""Entidad de dominio Tarea (ampliada en s06).

Unidad de trabajo del tablero. En s05 tenía id/titulo/descripcion/estado/proyecto_id;
en s06 se completa con responsable (N:1 por id, opcional), etiquetas (M:N por
`etiqueta_ids`) y timestamps. Los comentarios apuntan a la tarea desde Comentario.tarea_id
(N:1), no se anidan acá. Los campos nuevos tienen default para no romper el flujo de s05.
"""

from app.models.base import EntidadConTiempos
from app.models.estado import Estado


class Tarea(EntidadConTiempos):
    id: int | None = None
    titulo: str
    descripcion: str | None = None
    estado: Estado = Estado.BACKLOG
    proyecto_id: int = 1
    responsable_id: int | None = None  # N:1 con Usuario (opcional)
    etiqueta_ids: list[int] = []       # M:N con Etiqueta
