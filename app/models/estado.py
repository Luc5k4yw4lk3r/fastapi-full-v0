"""Estados posibles de una Tarea en el tablero de TaskFlow.

Un Enum de strings: FastAPI/Pydantic lo usan para validar la entrada (un estado
inválido devuelve 422 automáticamente) y define el flujo backlog -> en progreso -> hecho.
"""

from enum import Enum


class Estado(str, Enum):
    BACKLOG = "backlog"
    EN_PROGRESO = "en progreso"
    HECHO = "hecho"
