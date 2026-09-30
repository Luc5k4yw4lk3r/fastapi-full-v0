"""Capa router: endpoints HTTP de tareas (s05).

Traduce HTTP <-> dominio y delega toda la lógica en el service. Convierte las
excepciones de dominio en códigos HTTP (404 si no existe el proyecto/tarea). No accede a
datos ni contiene reglas de negocio. Endpoints: crear, listar y mover tarea.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.dependencies import obtener_servicio_tareas
from app.models.estado import Estado
from app.models.tarea import Tarea
from app.services.tarea_service import (
    ProyectoNoEncontrado,
    ServicioTareas,
    TareaNoEncontrada,
)

router = APIRouter(prefix="/tasks", tags=["tareas"])


class MoverTarea(BaseModel):
    """Cuerpo del endpoint de mover: solo el estado destino (validado por el Enum)."""

    estado: Estado


@router.post("", response_model=Tarea, status_code=status.HTTP_201_CREATED)
def crear_tarea(
    tarea: Tarea,
    servicio: ServicioTareas = Depends(obtener_servicio_tareas),
) -> Tarea:
    try:
        return servicio.crear_tarea(tarea)
    except ProyectoNoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El proyecto {tarea.proyecto_id} no existe",
        )


@router.get("", response_model=list[Tarea])
def listar_tareas(
    servicio: ServicioTareas = Depends(obtener_servicio_tareas),
) -> list[Tarea]:
    return servicio.listar_tareas()


@router.post("/{tarea_id}/move", response_model=Tarea)
def mover_tarea(
    tarea_id: int,
    cuerpo: MoverTarea,
    servicio: ServicioTareas = Depends(obtener_servicio_tareas),
) -> Tarea:
    try:
        return servicio.mover_tarea(tarea_id, cuerpo.estado)
    except TareaNoEncontrada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La tarea {tarea_id} no existe",
        )
