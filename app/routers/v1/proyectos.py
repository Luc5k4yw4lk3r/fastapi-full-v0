"""Router v1 de proyectos (s10): CRUD + tablero.

Delega en los services; las excepciones de dominio se traducen a HTTP mediante los
exception handlers registrados en app/main.py. Implementa el contrato de docs/api-v1.yaml.
"""

from fastapi import APIRouter, Depends, Query, Response, status

from app.models.estado import Estado
from app.models.proyecto import Proyecto
from app.routers.v1.dependencias import servicio_proyectos, servicio_tareas
from app.routers.v1.schemas import (
    ColumnasTablero,
    Pagina,
    ProyectoActualizar,
    ProyectoCrear,
    Tablero,
)
from app.services.proyecto_service import ServicioProyectos
from app.services.tarea_service import ServicioTareas

router = APIRouter(prefix="/proyectos", tags=["proyectos"])


@router.get("", response_model=Pagina[Proyecto])
def listar_proyectos(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    orden: str | None = None,
    sp: ServicioProyectos = Depends(servicio_proyectos),
) -> Pagina[Proyecto]:
    items, total = sp.listar_proyectos(orden=orden, limit=limit, offset=offset)
    return Pagina(total=total, limit=limit, offset=offset, items=items)


@router.post("", response_model=Proyecto, status_code=status.HTTP_201_CREATED)
def crear_proyecto(
    datos: ProyectoCrear,
    sp: ServicioProyectos = Depends(servicio_proyectos),
) -> Proyecto:
    proyecto = Proyecto(
        id=None, nombre=datos.nombre, equipo_id=datos.equipo_id, descripcion=datos.descripcion
    )
    return sp.crear_proyecto(proyecto)


@router.get("/{proyecto_id}", response_model=Proyecto)
def obtener_proyecto(
    proyecto_id: int, sp: ServicioProyectos = Depends(servicio_proyectos)
) -> Proyecto:
    return sp.obtener_proyecto(proyecto_id)


@router.patch("/{proyecto_id}", response_model=Proyecto)
def actualizar_proyecto(
    proyecto_id: int,
    datos: ProyectoActualizar,
    sp: ServicioProyectos = Depends(servicio_proyectos),
) -> Proyecto:
    return sp.actualizar_proyecto(proyecto_id, datos.model_dump(exclude_unset=True))


@router.delete("/{proyecto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_proyecto(
    proyecto_id: int, sp: ServicioProyectos = Depends(servicio_proyectos)
) -> Response:
    sp.eliminar_proyecto(proyecto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{proyecto_id}/tablero", response_model=Tablero)
def tablero_de_proyecto(
    proyecto_id: int,
    estado: Estado | None = None,
    responsable_id: int | None = None,
    etiqueta: str | None = None,
    orden: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    sp: ServicioProyectos = Depends(servicio_proyectos),
    st: ServicioTareas = Depends(servicio_tareas),
) -> Tablero:
    sp.obtener_proyecto(proyecto_id)  # valida existencia (404 si no está)
    items, _ = st.listar_tareas(
        proyecto_id=proyecto_id,
        estado=estado.value if estado else None,
        responsable_id=responsable_id,
        etiqueta=etiqueta,
        orden=orden,
        limit=limit,
        offset=offset,
    )
    columnas = ColumnasTablero()
    destino = {
        Estado.BACKLOG: columnas.backlog,
        Estado.EN_PROGRESO: columnas.en_progreso,
        Estado.HECHO: columnas.hecho,
    }
    for tarea in items:
        destino[tarea.estado].append(tarea)
    return Tablero(proyecto_id=proyecto_id, columnas=columnas)
