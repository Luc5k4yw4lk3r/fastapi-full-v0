"""Motor, sesión y base declarativa de SQLAlchemy (s07).

Configura la conexión a PostgreSQL a partir de DATABASE_URL (se pasa con
`uvicorn --env-file .env`). Expone:
- `Base`: clase declarativa de la que heredan los modelos ORM.
- `SessionLocal`: fábrica de sesiones síncronas.
- `get_db()`: dependencia de FastAPI que entrega una Session por request y garantiza
  su cierre (y rollback ante error) al terminar.
"""

import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# DATABASE_URL debe usar el driver de SQLAlchemy + psycopg3: postgresql+psycopg://
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://taskflow:taskflow@localhost:5432/taskflow",
)

# `future=True` es el default en SQLAlchemy 2.0; `pool_pre_ping` evita conexiones muertas.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base declarativa común de todos los modelos ORM."""


def get_db() -> Iterator[Session]:
    """Entrega una Session por request; hace rollback ante error y cierra siempre."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
