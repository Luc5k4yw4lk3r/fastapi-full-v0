"""Router v1 de usuarios (s10): lectura de apoyo para asignar responsables."""

from fastapi import APIRouter, Depends, Query

from app.models.usuario import Usuario
from app.routers.v1.dependencias import servicio_usuarios
from app.routers.v1.schemas import Pagina
from app.services.usuario_service import ServicioUsuarios

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=Pagina[Usuario])
def listar_usuarios(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    su: ServicioUsuarios = Depends(servicio_usuarios),
) -> Pagina[Usuario]:
    items, total = su.listar_usuarios(limit=limit, offset=offset)
    return Pagina(total=total, limit=limit, offset=offset, items=items)


@router.get("/{usuario_id}", response_model=Usuario)
def obtener_usuario(
    usuario_id: int, su: ServicioUsuarios = Depends(servicio_usuarios)
) -> Usuario:
    return su.obtener_usuario(usuario_id)
