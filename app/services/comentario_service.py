"""Capa service: comentarios de una tarea para la API v1 (s10).

Crear y listar comentarios, validando que la tarea y el autor existan. Controla la
transacción (commit/rollback) al crear. No conoce HTTP.
"""

from sqlalchemy.orm import Session

from app.models.comentario import Comentario
from app.repositories.comentario_repository import RepositorioComentariosSQL
from app.repositories.tarea_repository import RepositorioTareasSQL
from app.repositories.usuario_repository import RepositorioUsuariosSQL
from app.services.errores import TareaNoEncontrada, UsuarioNoEncontrado


class ServicioComentarios:
    def __init__(
        self,
        repo_comentarios: RepositorioComentariosSQL,
        repo_tareas: RepositorioTareasSQL,
        repo_usuarios: RepositorioUsuariosSQL,
        session: Session,
    ) -> None:
        self._repo = repo_comentarios
        self._repo_tareas = repo_tareas
        self._repo_usuarios = repo_usuarios
        self._session = session

    def crear_comentario(self, tarea_id: int, autor_id: int, texto: str) -> Comentario:
        if self._repo_tareas.obtener(tarea_id) is None:
            raise TareaNoEncontrada(tarea_id)
        if not self._repo_usuarios.existe(autor_id):
            raise UsuarioNoEncontrado(autor_id)
        comentario = Comentario(tarea_id=tarea_id, autor_id=autor_id, texto=texto)
        try:
            creado = self._repo.crear(comentario)
            self._session.commit()
            return creado
        except Exception:
            self._session.rollback()
            raise

    def listar_comentarios(
        self, tarea_id: int, *, limit: int = 20, offset: int = 0
    ) -> tuple[list[Comentario], int]:
        if self._repo_tareas.obtener(tarea_id) is None:
            raise TareaNoEncontrada(tarea_id)
        return self._repo.listar_por_tarea(tarea_id, limit=limit, offset=offset)
