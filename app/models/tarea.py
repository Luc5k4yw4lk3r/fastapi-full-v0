"""Entidad de dominio Tarea (mínima para s05).

Clase Pydantic única que viaja de punta a punta (router -> service -> repository),
según la decisión de trade-off de la sesión. Al crear, el cliente manda `titulo`
(y opcionalmente `descripcion`/`proyecto_id`); el `id` lo asigna el repositorio y el
`estado` arranca en BACKLOG. El modelo completo (responsable, comentarios...) es s06+.
"""

from pydantic import BaseModel

from app.models.estado import Estado


class Tarea(BaseModel):
    id: int | None = None
    titulo: str
    descripcion: str | None = None
    estado: Estado = Estado.BACKLOG
    proyecto_id: int = 1
