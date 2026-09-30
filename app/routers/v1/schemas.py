"""Schemas de request/response de la API v1 (s10).

Modelos Pydantic del borde HTTP: variantes Crear/Actualizar (distintas de las entidades
de dominio), la envoltura de paginación genérica y el tablero. Las respuestas de entidad
reusan los modelos de dominio (Tarea, Proyecto, ...).
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

from app.models.estado import Estado
from app.models.tarea import Tarea

T = TypeVar("T")


class Pagina(BaseModel, Generic[T]):
    """Envoltura paginada: items + metadata (total/limit/offset)."""

    total: int
    limit: int
    offset: int
    items: list[T]


# --- Proyectos ---
class ProyectoCrear(BaseModel):
    nombre: str
    equipo_id: int
    descripcion: str | None = None


class ProyectoActualizar(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None


# --- Tareas ---
class TareaCrear(BaseModel):
    titulo: str
    proyecto_id: int = 1
    descripcion: str | None = None
    responsable_id: int | None = None
    etiqueta_ids: list[int] = []


class TareaActualizar(BaseModel):
    titulo: str | None = None
    descripcion: str | None = None
    responsable_id: int | None = None
    etiqueta_ids: list[int] | None = None


class MoverTarea(BaseModel):
    estado: Estado


# --- Comentarios ---
class ComentarioCrear(BaseModel):
    autor_id: int
    texto: str


# --- Tablero ---
class ColumnasTablero(BaseModel):
    backlog: list[Tarea] = []
    en_progreso: list[Tarea] = []
    hecho: list[Tarea] = []


class Tablero(BaseModel):
    proyecto_id: int
    columnas: ColumnasTablero
