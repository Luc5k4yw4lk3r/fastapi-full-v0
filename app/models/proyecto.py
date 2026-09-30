"""Entidad de dominio Proyecto (mínima para s05).

Un proyecto agrupa tareas. En s05 vive en memoria y solo tiene id y nombre; el
modelo completo (con Equipo, dueño, etc.) se define en s06. Es una clase Pydantic
que, según la decisión de la sesión, se usa tanto en el dominio como en el borde HTTP.
"""

from pydantic import BaseModel


class Proyecto(BaseModel):
    id: int
    nombre: str
