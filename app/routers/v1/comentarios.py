"""Router v1 de comentarios (s10): listar y crear por tarea.

Rutas anidadas bajo /tareas/{id}/comentarios. Delega en ServicioComentarios.
"""

from fastapi import APIRouter, Depends, Query, status

from app.models.comentario import Comentario
from app.routers.v1.dependencias import servicio_comentarios
from app.routers.v1.schemas import ComentarioCrear, Pagina
from app.services.comentario_service import ServicioComentarios

router = APIRouter(prefix="/tareas/{tarea_id}/comentarios", tags=["comentarios"])


@router.get("", response_model=Pagina[Comentario])
def listar_comentarios(
    tarea_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sc: ServicioComentarios = Depends(servicio_comentarios),
) -> Pagina[Comentario]:
    items, total = sc.listar_comentarios(tarea_id, limit=limit, offset=offset)
    return Pagina(total=total, limit=limit, offset=offset, items=items)


@router.post("", response_model=Comentario, status_code=status.HTTP_201_CREATED)
def crear_comentario(
    tarea_id: int,
    datos: ComentarioCrear,
    sc: ServicioComentarios = Depends(servicio_comentarios),
) -> Comentario:
    return sc.crear_comentario(tarea_id, datos.autor_id, datos.texto)
