"""Routers de la API v1 (s10).

Agrupa los routers por recurso bajo el prefijo /v1, según el contrato de docs/api-v1.yaml.
`router` es el APIRouter agregador que monta app/main.py.
"""

from fastapi import APIRouter

from app.routers.v1 import comentarios, etiquetas, proyectos, tareas, usuarios

router = APIRouter(prefix="/v1")
router.include_router(proyectos.router)
router.include_router(tareas.router)
router.include_router(comentarios.router)
router.include_router(usuarios.router)
router.include_router(etiquetas.router)
