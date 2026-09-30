"""Entidad de dominio Comentario (s06).

Mensaje que un usuario deja en una tarea. Relaciones N:1 por id: pertenece a una tarea
(`tarea_id`) y tiene un autor (`autor_id`). Los timestamps sirven para ordenar el hilo
cronológicamente. Sin persistencia (se conecta en s07).
"""

from app.models.base import EntidadConTiempos


class Comentario(EntidadConTiempos):
    id: int | None = None  # lo asigna el repositorio al crear
    tarea_id: int
    autor_id: int
    texto: str
