"""Capa service: lectura de usuarios para la API v1 (s10).

Apoyo para asignar responsables: listar y obtener. Solo lectura.
"""

from app.models.usuario import Usuario
from app.repositories.usuario_repository import RepositorioUsuariosSQL
from app.services.errores import UsuarioNoEncontrado


class ServicioUsuarios:
    def __init__(self, repo_usuarios: RepositorioUsuariosSQL) -> None:
        self._repo = repo_usuarios

    def listar_usuarios(self, *, limit: int = 20, offset: int = 0) -> tuple[list[Usuario], int]:
        return self._repo.listar(limit=limit, offset=offset)

    def obtener_usuario(self, usuario_id: int) -> Usuario:
        usuario = self._repo.obtener(usuario_id)
        if usuario is None:
            raise UsuarioNoEncontrado(usuario_id)
        return usuario
