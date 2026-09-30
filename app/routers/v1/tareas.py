"""Router v1 de tareas (s10): CRUD + mover estado.

Delega en ServicioTareas; las excepciones de dominio se traducen a HTTP en los handlers
de app/main.py. Implementa el contrato de docs/api-v1.yaml.
"""

from fastapi import APIRouter, Depends, Query, Response, status

from app.models.estado import Estado
from app.models.tarea import Tarea
from app.routers.v1.dependencias import servicio_tareas
from app.routers.v1.schemas import MoverTarea, Pagina, TareaActualizar, TareaCrear
from app.services.tarea_service import ServicioTareas

router = APIRouter(prefix="/tareas", tags=["tareas"])


@router.get("", response_model=Pagina[Tarea])
def listar_tareas(
    proyecto_id: int | None = None,
    estado: Estado | None = None,
    responsable_id: int | None = None,
    etiqueta: str | None = None,
    orden: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    st: ServicioTareas = Depends(servicio_tareas),
) -> Pagina[Tarea]:
    items, total = st.listar_tareas(
        proyecto_id=proyecto_id,
        estado=estado.value if estado else None,
        responsable_id=responsable_id,
        etiqueta=etiqueta,
        orden=orden,
        limit=limit,
        offset=offset,
    )
    return Pagina(total=total, limit=limit, offset=offset, items=items)


@router.post("", response_model=Tarea, status_code=status.HTTP_201_CREATED)
def crear_tarea(datos: TareaCrear, st: ServicioTareas = Depends(servicio_tareas)) -> Tarea:
    tarea = Tarea(
        titulo=datos.titulo,
        descripcion=datos.descripcion,
        proyecto_id=datos.proyecto_id,
        responsable_id=datos.responsable_id,
        etiqueta_ids=datos.etiqueta_ids,
    )
    return st.crear_tarea(tarea)


@router.get("/{tarea_id}", response_model=Tarea)
def obtener_tarea(tarea_id: int, st: ServicioTareas = Depends(servicio_tareas)) -> Tarea:
    return st.obtener_tarea(tarea_id)


@router.patch("/{tarea_id}", response_model=Tarea)
def actualizar_tarea(
    tarea_id: int,
    datos: TareaActualizar,
    st: ServicioTareas = Depends(servicio_tareas),
) -> Tarea:
    return st.actualizar_tarea(tarea_id, datos.model_dump(exclude_unset=True))


@router.delete("/{tarea_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tarea(tarea_id: int, st: ServicioTareas = Depends(servicio_tareas)) -> Response:
    st.eliminar_tarea(tarea_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{tarea_id}/mover", response_model=Tarea)
def mover_tarea(
    tarea_id: int,
    cuerpo: MoverTarea,
    st: ServicioTareas = Depends(servicio_tareas),
) -> Tarea:
    return st.mover_tarea(tarea_id, cuerpo.estado)
