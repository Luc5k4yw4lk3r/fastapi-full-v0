"""Router v1 de etiquetas (s10): lectura de apoyo para clasificar tareas."""

from fastapi import APIRouter, Depends

from app.models.etiqueta import Etiqueta
from app.routers.v1.dependencias import servicio_etiquetas
from app.services.etiqueta_service import ServicioEtiquetas

router = APIRouter(prefix="/etiquetas", tags=["etiquetas"])


@router.get("", response_model=list[Etiqueta])
def listar_etiquetas(
    se: ServicioEtiquetas = Depends(servicio_etiquetas),
) -> list[Etiqueta]:
    return se.listar_etiquetas()
