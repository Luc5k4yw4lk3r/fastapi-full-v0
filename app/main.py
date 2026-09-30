"""Punto de entrada de la aplicación TaskFlow (s05).

Crea la instancia de FastAPI que levanta Uvicorn y monta el router de tareas. Es la
"cima" de la arquitectura en capas: acá se ensambla todo, pero no hay lógica de negocio.
En s05 todo el estado vive en memoria; la conexión a PostgreSQL llega en s07.
"""

from fastapi import FastAPI

from app.routers import tareas

app = FastAPI(title="TaskFlow", version="0.5.0")

app.include_router(tareas.router)


@app.get("/health", tags=["infra"])
def health() -> dict[str, str]:
    """Chequeo simple para verificar que el servidor responde."""
    return {"status": "ok"}
