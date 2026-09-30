"""Modelos de vista para el endpoint de lectura de agentes (s08).

Son DTOs de RESPUESTA (no entidades de dominio): describen un tablero autocontenido,
con el contexto ya resuelto (nombres en vez de ids, tareas agrupadas por columna, con
responsable, etiquetas y comentarios). Pensados para que un agente entienda el estado
del proyecto en una sola llamada, sin tener que resolver relaciones por su cuenta.
"""

from datetime import datetime

from pydantic import BaseModel


class EquipoVista(BaseModel):
    nombre: str


class EtiquetaVista(BaseModel):
    nombre: str
    color: str | None = None


class ComentarioVista(BaseModel):
    autor: str
    texto: str
    fecha: datetime | None = None


class TareaVista(BaseModel):
    id: int
    titulo: str
    descripcion: str | None = None
    responsable: str | None = None  # nombre, no id
    etiquetas: list[EtiquetaVista] = []
    comentarios: list[ComentarioVista] = []


class ColumnasTablero(BaseModel):
    backlog: list[TareaVista] = []
    en_progreso: list[TareaVista] = []
    hecho: list[TareaVista] = []


class ProyectoVista(BaseModel):
    id: int
    nombre: str
    descripcion: str | None = None
    equipo: EquipoVista


class ResumenTablero(BaseModel):
    total_tareas: int
    por_estado: dict[str, int]


class TableroAgente(BaseModel):
    """Respuesta autocontenida del tablero de un proyecto, lista para un agente."""

    generado_en: datetime  # marca de frescura: cuándo se armó esta vista
    proyecto: ProyectoVista
    resumen: ResumenTablero
    columnas: ColumnasTablero
