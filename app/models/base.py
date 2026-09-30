"""Base común de las entidades de dominio (s06).

Agrupa los campos de auditoría (created_at / updated_at) para no repetirlos en cada
entidad. Son opcionales: en s06 el modelo solo los declara; los valores reales los
poblará la capa de persistencia en s07. El resto de las entidades hereda de acá.
"""

from datetime import datetime

from pydantic import BaseModel


class EntidadConTiempos(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None
