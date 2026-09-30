"""Repositorio de tareas en memoria (s05).

Guarda las tareas en un dict indexado por id (búsqueda/actualización O(1), igual que
después será buscar por PK en la BD) y lleva un contador para asignar ids. Encapsula el
almacenamiento tras una interfaz estable: el service no sabe si por dentro hay memoria o
Postgres. En s07 se reemplaza por una versión con ORM sin tocar service ni router.
"""

from app.models.tarea import Tarea


class RepositorioTareasEnMemoria:
    def __init__(self) -> None:
        self._tareas: dict[int, Tarea] = {}
        self._siguiente_id: int = 1

    def crear(self, tarea: Tarea) -> Tarea:
        tarea.id = self._siguiente_id  # el id lo asigna el repositorio, no el cliente
        self._tareas[tarea.id] = tarea
        self._siguiente_id += 1
        return tarea

    def listar(self) -> list[Tarea]:
        return list(self._tareas.values())

    def obtener(self, tarea_id: int) -> Tarea | None:
        return self._tareas.get(tarea_id)

    def guardar(self, tarea: Tarea) -> Tarea:
        # Persiste una tarea ya existente (p. ej. tras cambiarle el estado).
        self._tareas[tarea.id] = tarea
        return tarea
