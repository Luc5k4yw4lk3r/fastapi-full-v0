"""Capa router: endpoint de lectura para agentes (s08).

Expone una vista autocontenida del tablero de un proyecto, pensada para consumo por un
agente: en una sola llamada devuelve el proyecto, su equipo y las tareas agrupadas por
columna con responsable, etiquetas y comentarios ya resueltos. Sin versionar todavía
(el `/v1` es s09). Delega en el service y traduce ProyectoNoEncontrado a 404.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.tablero import TableroAgente
from app.repositories.tablero_repository import RepositorioTableroSQL
from app.services.tablero_service import ServicioTablero
from app.services.errores import ProyectoNoEncontrado

router = APIRouter(prefix="/agent", tags=["agentes"])


def obtener_servicio_tablero(db: Session = Depends(get_db)) -> ServicioTablero:
    return ServicioTablero(RepositorioTableroSQL(db))


@router.get("/proyectos/{proyecto_id}/tablero", response_model=TableroAgente)
def tablero_de_proyecto(
    proyecto_id: int,
    servicio: ServicioTablero = Depends(obtener_servicio_tablero),
) -> TableroAgente:
    try:
        return servicio.tablero_de_proyecto(proyecto_id)
    except ProyectoNoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El proyecto {proyecto_id} no existe",
        )
